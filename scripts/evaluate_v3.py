"""V3 — val threshold sweep + single frozen-test scoring + latency probe (100-class).

Reads tensors_100_real / split_idx_100 / scaler_100_real and the winner
 weights from EXP-2026-003-{arch}-full. Writes policy.json, test_report.json,
per_class.csv, confusion.npz into the winner EXP dir. Single scored run only.
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

P = argparse.ArgumentParser()
P.add_argument("--arch", choices=["lstm", "gru"], default="lstm")
A = P.parse_args()

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
import tensorflow as tf
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

D = np.load(ROOT / "data/dataset/processed/tensors_100_real.npz")
S = np.load(ROOT / "data/dataset/processed/split_idx_100.npz")
SC = np.load(ROOT / "models/scaler_100_real.npz")
Xs = ((D["X"].astype("float32") - SC["mean"]) / SC["std"]).astype("float32")
y = D["y"]
va, te = S["val"], S["test"]
EXP = ROOT / "models" / f"EXP-2026-003-{A.arch}-full"

model = tf.keras.models.load_model(EXP / f"SBAI-MDL-ISL-3.0.0_{A.arch}.keras")
pv = model.predict(Xs[va], verbose=0)
yv = y[va]

# threshold sweep on VAL only
best = (0, 0, 0, 0)
for thr in [round(x * 0.05, 2) for x in range(8, 20)]:
    conf = pv.max(1)
    pred = pv.argmax(1)
    accepted = conf >= thr
    cov = float(accepted.mean())
    acc = float(accuracy_score(yv[accepted], pred[accepted])) if accepted.any() else 0.0
    score = acc * cov
    if score > best[0]:
        best = (score, thr, acc, cov)
_, thr, vacc, vcov = best
policy = {"threshold": thr, "smoothing_window": 5, "val_accepted_acc": round(vacc, 4),
          "val_coverage": round(vcov, 4),
          "states": ["Accepted", "Uncertain", "No-Sign", "Tracking-Lost"]}
(EXP / "policy.json").write_text(json.dumps(policy, indent=1))
print("policy:", json.dumps(policy), flush=True)

# single frozen-test scoring
t0 = time.perf_counter()
pt = model.predict(Xs[te], verbose=0)
infer_ms = (time.perf_counter() - t0) / len(te) * 1000
yt = y[te]
yp = pt.argmax(1)
acc = float(accuracy_score(yt, yp))
f1 = float(f1_score(yt, yp, average="macro", zero_division=0))
prec, rec, f1c, sup = precision_recall_fscore_support(yt, yp, labels=list(range(100)), zero_division=0)
cm = confusion_matrix(yt, yp, labels=list(range(100)))
np.save(EXP / "confusion.npy", cm)
meta = json.loads((ROOT / "data/dataset/processed/tensors_100_real.json").read_text())
idx2cid = {v: k for k, v in meta["class_index"].items()}
with (EXP / "per_class.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["index", "class_id", "precision", "recall", "f1", "support"])
    for i in range(100):
        w.writerow([i, idx2cid[i], round(float(prec[i]), 4), round(float(rec[i]), 4),
                    round(float(f1c[i]), 4), int(sup[i])])

# latency probe: per-sample p50/p95/p99 + sustained FPS (batch=1, 200 samples)
probe_n = min(200, len(te))
t0 = time.perf_counter()
for i in range(probe_n):
    model.predict(Xs[te[i : i + 1]], verbose=0)
wall = time.perf_counter() - t0
import time as _t
ts = []
for i in range(probe_n):
    s = _t.perf_counter()
    model.predict(Xs[te[i : i + 1]], verbose=0)
    ts.append((_t.perf_counter() - s) * 1000)
ts.sort()
lat = {"p50_ms": round(ts[len(ts) // 2], 2), "p95_ms": round(ts[int(len(ts) * 0.95)], 2),
       "p99_ms": round(ts[int(len(ts) * 0.99)], 2), "fps": round(probe_n / wall, 1)}
report = {"accuracy": round(acc, 4), "macro_f1": round(f1, 4), "n_test": len(te),
          "threshold": thr, "latency": lat}
(EXP / "test_report.json").write_text(json.dumps(report, indent=1))
print("test:", json.dumps(report), flush=True)
print("EVAL OK", flush=True)
