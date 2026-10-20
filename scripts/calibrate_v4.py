"""VAL-only confidence calibration: temperature scaling + decision thresholds.

Single fitting entry point for the three-state policy (Task 2 of
Docs/plans/2026-10-19-realtime-accuracy-calibration.md). Fits ONCE on the
SPLIT-109 validation split (n=2397, signer-disjoint) and writes two artifacts
next to the ACTIVE model:

  models/<active>/calibration.json   {temperature, val_nll, ECE/Brier before
                                      & after, fit_rejected, ...}
  models/<active>/policy.json        merge-write: accept_threshold,
                                      provisional_threshold, tta_windows=1,
                                      val_accepted_accuracy, val_coverage,
                                      updated_by; legacy "threshold" is set
                                      equal to accept_threshold.

No test data is ever read here (TEST is evaluated once in Task 8).

Threshold rules (on CALIBRATED val confs; grid 0.00..0.99 step 0.01):
  precision(t) := argmax-accuracy among val samples with conf >= t
                  (0.0 when no sample qualifies)
  t_accept     := min t with precision(t) >= 0.90, else 0.99
  t_prov       := min t with precision(t) >= 0.80, else max(t_accept-0.10, 0)
  clamp        := t_prov = max(min(t_prov, t_accept - 0.01), 0)
  NOTE: precision(conf >= 0.00) IS the val argmax accuracy, so whenever that
  is >= 0.80 the literal rule yields t_prov = 0 (the provisional band then
  spans the whole non-accept region; the "uncertain" state exists for
  policies without provisional_threshold and for the <0.80 fallback case).
  This is reported in the printed output and in M13 section 5.

Usage:
  py -3 scripts/calibrate_v4.py
"""
from __future__ import annotations

import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import deps  # noqa: E402

GRID = [i / 100 for i in range(100)]
T_GRID = np.exp(np.linspace(np.log(0.25), np.log(4.0), 151))
PREC_ACCEPT = 0.90
PREC_PROV = 0.80
N_ECE_BINS = 15


def _ece(conf: np.ndarray, ok: np.ndarray, bins: int = N_ECE_BINS) -> float:
    ece = 0.0
    edges = np.linspace(0.0, 1.0, bins + 1)
    for b in range(bins):
        lo, hi = edges[b], edges[b + 1]
        m = (conf >= lo) & ((conf < hi) if b < bins - 1 else (conf <= hi))
        if not m.any():
            continue
        ece += (int(m.sum()) / len(conf)) * abs(float(ok[m].mean()) - float(conf[m].mean()))
    return float(ece)


def _brier(p: np.ndarray, y: np.ndarray, n_class: int) -> float:
    onehot = np.zeros_like(p)
    onehot[np.arange(len(y)), y] = 1.0
    return float(np.mean(np.sum((p - onehot) ** 2, axis=1)))


def _nll(p: np.ndarray, y: np.ndarray) -> float:
    return float(-np.mean(np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1.0))))


def _softmax_temp(logp: np.ndarray, T: float) -> np.ndarray:
    z = logp / T
    e = np.exp(z - np.max(z, axis=1, keepdims=True))
    return e / np.sum(e, axis=1, keepdims=True)


def _precision(conf: np.ndarray, ok: np.ndarray, t: float) -> float:
    m = conf >= t
    return float(ok[m].mean()) if m.any() else 0.0


def main() -> None:
    assert deps.uses_ensemble(), "calibrate_v4 expects the active model to be an ensemble"
    model_id = deps.model_version()

    D = np.load(ROOT / "data/dataset/processed" / "tensors_109_real.npz")
    S = np.load(ROOT / "data/dataset/processed" / "split_idx_109.npz")
    mu, sd = deps.get_scaler()
    Xv = ((D["X"][S["val"]].astype("float32") - mu) / sd).astype("float32")
    y = D["y"][S["val"]].astype(int)
    n = len(y)
    print(f"[calibrate_v4] model={model_id} val_n={n} (split=val only)", flush=True)

    # 1) RAW (uncalibrated) ensemble probs on val — temperature is fit HERE.
    print("[calibrate_v4] infer_ensemble over val (raw) ...", flush=True)
    raw = np.concatenate(
        [deps.infer_ensemble(Xv[s:s + 512]) for s in range(0, n, 512)],
        axis=0,
    ).astype("float32")
    ci = raw.argmax(1)
    ok = ci == y
    logp = np.log(np.clip(raw, 1e-12, 1.0))

    ece_before = _ece(raw.max(1), ok)
    brier_before = _brier(raw, y, raw.shape[1])

    # 2) Temperature: grid minimizing val NLL; rejected if ECE does not improve.
    best_T, best_nll = 1.0, _nll(raw, y)
    for T in T_GRID:
        p = _softmax_temp(logp, float(T))
        nll = _nll(p, y)
        if nll < best_nll:
            best_T, best_nll = float(T), nll
    p_best = _softmax_temp(logp, best_T)
    ece_at_T = _ece(p_best.max(1), ok)
    if ece_at_T >= ece_before:
        T_final, fit_rejected = 1.0, True
    else:
        T_final, fit_rejected = best_T, False
    probs = raw if T_final == 1.0 else _softmax_temp(logp, T_final)
    val_nll = _nll(probs, y)
    ece_after = _ece(probs.max(1), ok)
    brier_after = _brier(probs, y, probs.shape[1])

    # 3) Thresholds on CALIBRATED val confs (argmax is temperature-invariant).
    conf = probs.max(1)
    t_accept = next((t for t in GRID if _precision(conf, ok, t) >= PREC_ACCEPT), 0.99)
    t_prov = next((t for t in GRID if _precision(conf, ok, t) >= PREC_PROV),
                  max(t_accept - 0.10, 0.0))
    t_prov = max(min(t_prov, t_accept - 0.01), 0.0)
    assert 0.0 <= t_prov < t_accept <= 0.99, (t_prov, t_accept)

    acc_at_accept = _precision(conf, ok, t_accept)
    coverage = float((conf >= t_accept).mean())

    # 4) Merge-write policy.json (preserve unrelated keys; legacy key mirrors accept).
    policy_path = deps.MODELS / model_id / "policy.json"
    policy = json.loads(policy_path.read_text())
    policy.update({
        "accept_threshold": round(t_accept, 2),
        "provisional_threshold": round(t_prov, 2),
        "tta_windows": 1,
        "val_accepted_accuracy": round(acc_at_accept, 6),
        "val_coverage": round(coverage, 6),
        "updated_by": "calibrate_v4",
    })
    policy["threshold"] = policy["accept_threshold"]
    policy_path.write_text(json.dumps(policy, indent=2) + "\n")

    # 5) calibration.json schema (pinned in the plan's Interfaces block).
    calibration = {
        "model_id": model_id,
        "temperature": round(T_final, 6),
        "fitted_on": "val",
        "val_nll": round(val_nll, 6),
        "val_ece_before": round(ece_before, 6),
        "val_ece_after": round(ece_after, 6),
        "val_brier_before": round(brier_before, 6),
        "val_brier_after": round(brier_after, 6),
        "fit_rejected": fit_rejected,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (deps.MODELS / model_id / "calibration.json").write_text(
        json.dumps(calibration, indent=2) + "\n"
    )

    verdict = "fit_rejected -> temperature=1.0 (ECE did not improve)" if fit_rejected else \
        f"temperature={T_final:.4f} (ECE {ece_before:.4f} -> {ece_after:.4f})"
    print(f"[calibrate_v4] {verdict}", flush=True)
    print(f"[calibrate_v4] Brier {brier_before:.4f} -> {brier_after:.4f}; "
          f"val NLL {val_nll:.4f}", flush=True)
    print(f"[calibrate_v4] t_accept={t_accept:.2f} (precision {acc_at_accept:.4f}, "
          f"coverage {coverage:.4f}) t_prov={t_prov:.2f}", flush=True)
    print(f"[calibrate_v4] band check OK: 0 <= {t_prov:.2f} < {t_accept:.2f} <= 0.99",
          flush=True)
    if t_prov == 0.0:
        print("[calibrate_v4] NOTE: t_prov=0 by the literal precision rule "
              "(val argmax accuracy >= 0.80 at conf>=0); the provisional band "
              "spans the whole non-accept region and 'uncertain' never fires "
              "under this fitted policy.", flush=True)


if __name__ == "__main__":
    main()
