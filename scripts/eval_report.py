"""Offline VAL/TEST accuracy & decision-policy report (M13 baseline harness).

Loads the frozen SPLIT-109 tensors, scales rows with the ACTIVE backend
scaler (same (X - mean) / std formula as scripts/evaluate_v3.py — X in the
npz is RAW), runs the ACTIVE backend ensemble in chunks of 512, and prints
/ writes the pinned metric keys consumed by Docs/M13_ACCURACY_CALIBRATION.md.

Task 1 semantics (later tasks extend, not redefine):
  - probabilities = deps.recognize_probs_batch (VAL-fitted temperature from
    models/<active>/calibration.json; identity until Task 2 runs)
  - status = deps.decision_status(conf, policy) — three-state
    recognized/provisional/uncertain (Task 3+)
  - TTA: --windows N runs multi-window inference (make_windows crops, raw
    outputs averaged, calibration once — Task 5); latency probe measures the
    same windows-aware path so w1 vs w3 gate comparisons are apples-to-apples

Usage:
  py -3 scripts/eval_report.py --split val --out Docs/eval/01_baseline_val.json --self-check
  py -3 scripts/eval_report.py --split test --confusion --per-class
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

P = argparse.ArgumentParser(description=__doc__)
P.add_argument("--split", choices=["val", "test"], required=True)
P.add_argument("--windows", type=int, default=1, choices=[1, 3],
               help="TTA window count: 1 (full only) or 3 (full/early/late crops)")
P.add_argument("--confusion", action="store_true",
               help="Also write a 109x109 confusion CSV next to --out")
P.add_argument("--per-class", action="store_true",
               help="Also write a per-class metrics CSV next to --out")
P.add_argument("--out", type=str, default=None, help="Metrics JSON output path")
P.add_argument("--self-check", action="store_true",
               help="Verify first 200 chunked probs match a naive per-row loop")
P.add_argument("--seed", type=int, default=0, help="Latency-probe sampling seed")
A = P.parse_args()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app import deps  # noqa: E402

D = np.load(ROOT / "data/dataset/processed" / "tensors_109_real.npz")
S = np.load(ROOT / "data/dataset/processed" / "split_idx_109.npz")
X_all, y_all = D["X"], D["y"]
idx = S[A.split]

mu, sd = deps.get_scaler()
Xs = ((X_all[idx].astype("float32") - mu) / sd).astype("float32")
y = y_all[idx].astype(int)
n = len(idx)
policy = deps.get_policy()
accept_thr = float(policy.get("accept_threshold", policy.get("threshold", 0.4)))
prov_thr = float(policy.get("provisional_threshold", accept_thr))

# ---- probabilities (calibrated, chunked, windows-aware TTA via
# recognize_probs_batch: raw outputs averaged over the k views, calibration
# applied once) ----
probs = deps.recognize_probs_batch(Xs, windows=A.windows)

# ---- self-check: first 200 rows vs naive per-row loop (same windows) ----
if A.self_check:
    k = min(200, n)
    naive = np.stack([deps.recognize_probs(Xs[i], A.windows) for i in range(k)])
    max_diff = float(np.abs(probs[:k] - naive).max())
    assert max_diff <= 1e-5, f"self-check FAILED: max |diff| = {max_diff}"
    print(f"SELF-CHECK OK (first {k} rows, max |diff| = {max_diff:.3e})", flush=True)

# ---- decisions (three-state via deps.decision_status; no-sign gate
# short-circuits exactly like predict.py/stream.py do before decisions) ----
pred = probs.argmax(1)
conf = probs.max(1)
correct = pred == y
# energy gate (pre-norm in the backend); on scaled npz rows this is ~always 0
no_sign = np.abs(Xs).max(axis=(1, 2)) < deps.NOSIGN_ENERGY
statuses = np.array([
    "no_sign" if g else deps.decision_status(float(c), policy)
    for c, g in zip(conf, no_sign)
])
recognized = statuses == "recognized"

n_rec = int((statuses == "recognized").sum())
n_prov = int((statuses == "provisional").sum())
n_unc = int((statuses == "uncertain").sum())

overall_correct = int((recognized & correct).sum())
accepted_correct = int((recognized & correct).sum())


def _macro_f1(y_true: np.ndarray, y_pred: np.ndarray, n_class: int = 109) -> float:
    f1s = []
    for c in range(n_class):
        tp = int(((y_pred == c) & (y_true == c)).sum())
        fp = int(((y_pred == c) & (y_true != c)).sum())
        fn = int(((y_pred != c) & (y_true == c)).sum())
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return float(np.mean(f1s))


def _ece(confidence: np.ndarray, ok: np.ndarray, bins: int = 15) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for b in range(bins):
        lo, hi = edges[b], edges[b + 1]
        mask = (confidence >= lo) & ((confidence < hi) if b < bins - 1 else (confidence <= hi))
        nb = int(mask.sum())
        if nb:
            ece += (nb / len(confidence)) * abs(float(ok[mask].mean()) - float(confidence[mask].mean()))
    return float(ece)


def _brier(probs_mat: np.ndarray, y_true: np.ndarray, n_class: int) -> float:
    onehot = np.zeros_like(probs_mat)
    onehot[np.arange(len(y_true)), y_true] = 1.0
    return float(np.mean(np.sum((probs_mat - onehot) ** 2, axis=1)))


# ---- latency probe: per-row windows-aware recognize path over 200 sampled
# split rows (make_windows + k model passes + calibration — the same cost a
# live request pays server-side, so --windows 1 vs 3 gate numbers compare
# apples-to-apples) ----
probe_n = min(200, n)
probe_i = np.random.default_rng(A.seed).choice(n, probe_n, replace=False)
lat_ms = []
for i in probe_i:
    t0 = time.perf_counter()
    deps.recognize_probs(Xs[i], A.windows)
    lat_ms.append((time.perf_counter() - t0) * 1000)
lat_ms.sort()
lat_p50 = float(lat_ms[len(lat_ms) // 2])
lat_p95 = float(lat_ms[min(int(len(lat_ms) * 0.95), len(lat_ms) - 1)])

n_class = int(probs.shape[1])
argmax_acc = float(correct.mean())
overall_acc = overall_correct / n if n else 0.0
accepted_acc = accepted_correct / n_rec if n_rec else 0.0
coverage = n_rec / n if n else 0.0
far_overall = int((recognized & ~correct).sum()) / n if n else 0.0
far_accepted = int((recognized & ~correct).sum()) / n_rec if n_rec else 0.0
low_conf_correct = int((correct & ~recognized).sum()) / max(int(correct.sum()), 1)

report = {
    "split": A.split,
    "n": int(n),
    "temperature": round(float(deps.get_calibration().get("temperature", 1.0)), 6),
    "tta_windows": int(A.windows),
    "thresholds": {"accept": accept_thr, "provisional": prov_thr},
    "argmax_accuracy": round(argmax_acc, 6),
    "overall_accuracy": round(overall_acc, 6),
    "accepted_accuracy": round(accepted_acc, 6),
    "coverage": round(coverage, 6),
    "false_accept_rate_overall": round(far_overall, 6),
    "false_accept_rate_accepted": round(far_accepted, 6),
    "low_conf_correct_rate": round(low_conf_correct, 6),
    "macro_f1": round(_macro_f1(y, pred, n_class), 6),
    "ece": round(_ece(conf, correct, 15), 6),
    "brier": round(_brier(probs, y, n_class), 6),
    "latency_ms": {"p50": round(lat_p50, 2), "p95": round(lat_p95, 2)},
    "counts": {"recognized": n_rec, "provisional": n_prov,
               "uncertain": n_unc, "no_sign": int(no_sign.sum())},
}
assert sum(report["counts"].values()) == n, "counts must sum to n"

if A.out:
    out_path = Path(A.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out_path}", flush=True)

if A.confusion:
    cm = np.zeros((n_class, n_class), dtype=int)
    np.add.at(cm, (y, pred), 1)
    cm_path = (Path(A.out).with_name(Path(A.out).stem + "_confusion.csv")
               if A.out else ROOT / "Docs" / "eval" / f"{A.split}_confusion.csv")
    cm_path.parent.mkdir(parents=True, exist_ok=True)
    class_ids = [c["class_id"] for c in deps.class_list()]
    with cm_path.open("w", newline="", encoding="utf-8") as fh:
        fh.write("true\\pred," + ",".join(class_ids) + "\n")
        for i, row in enumerate(cm):
            fh.write(class_ids[i] + "," + ",".join(map(str, row)) + "\n")
    print(f"wrote {cm_path}", flush=True)

if A.per_class:
    pc_path = (Path(A.out).with_name(Path(A.out).stem + "_per_class.csv")
               if A.out else ROOT / "Docs" / "eval" / f"{A.split}_per_class.csv")
    pc_path.parent.mkdir(parents=True, exist_ok=True)
    class_ids = [c["class_id"] for c in deps.class_list()]
    with pc_path.open("w", newline="", encoding="utf-8") as fh:
        fh.write("class_id,support,predicted,precision,recall,f1\n")
        for c in range(n_class):
            tp = int(((pred == c) & (y == c)).sum())
            support = int((y == c).sum())
            n_pred = int((pred == c).sum())
            prec = tp / n_pred if n_pred else 0.0
            rec = tp / support if support else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
            fh.write(f"{class_ids[c]},{support},{n_pred},{prec:.4f},{rec:.4f},{f1:.4f}\n")
    print(f"wrote {pc_path}", flush=True)

print(json.dumps(report, indent=1), flush=True)
print("EVAL REPORT OK", flush=True)
