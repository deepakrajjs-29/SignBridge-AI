"""T3.2/T3.3 — val threshold sweep + single frozen-test scoring + latency probe."""
import argparse, csv, json, sys, time
from pathlib import Path
import numpy as np

P = argparse.ArgumentParser()
P.add_argument("--arch", choices=["lstm", "gru"], default="lstm")
A = P.parse_args()

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

D = np.load(ROOT / "data/dataset/processed/tensors_mvp50.npz")
S = np.load(ROOT / "data/dataset/processed/split_idx.npz")
SC = np.load(ROOT / "models/scaler_mvp50.npz")
Xs = ((D["X"].astype("float32") - SC["mean"]) / SC["std"]).astype("float32")
y = D["y"]
va, te = S["val"], S["test"]
EXP = ROOT / "models" / f"EXP-2026-001-{A.arch}-full"
EXP.mkdir(parents=True, exist_ok=True)

model = tf.keras.models.load_model(EXP / f"SBAI-MDL-ISL-1.0.0_{A.arch}.keras")
pv = model.predict(Xs[va], verbose=0)
yv = y[va]

# T3.2: threshold sweep on VAL only (Accepted vs Uncertain)
best = (0, 0, 0)
for thr in [round(x * 0.05, 2) for x in range(8, 20)]:
    conf = pv.max(1)
    pred = pv.argmax(1)
    accepted = conf >= thr
    cov = float(accepted.mean())
    acc = float(accuracy_score(yv[accepted], pred[accepted])) if accepted.any() else 0.0
    score = acc * cov  # accepted-accuracy mass
    if score > best[0]:
        best = (score, thr, acc, cov)
_, thr, vacc, vcov = best
policy = {"threshold": thr, "smoothing_window": 5, "val_accepted_acc": round(vacc, 4),
          "val_coverage": round(vcov, 4),
          "states": ["Accepted", "Uncertain", "No-Sign", "Tracking-Lost"]}
(EXP / "policy.json").write_text(json.dumps(policy, indent=1))
print("policy:", json.dumps(policy))

# T3.3: SINGLE frozen-test scoring
t0 = time.time()
pt = model.predict(Xs[te], verbose=0)
infer_ms = (time.time() - t0) / len(te) * 1000
yt = y[te]
yp = pt.argmax(1)
acc = float(accuracy_score(yt, yp))
mf1 = float(f1_score(yt, yp, average="macro", zero_division=0))
prec, rec, f1c, _ = precision_recall_fscore_support(yt, yp, zero_division=0)
per_class = [{"idx": int(i), "p": round(float(prec[i]), 4), "r": round(float(rec[i]), 4),
              "f1": round(float(f1c[i]), 4)} for i in range(len(prec))]
with (EXP / "per_class.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["idx", "p", "r", "f1"])
    w.writeheader(); w.writerows(per_class)
worst = sorted(per_class, key=lambda r: r["f1"])[:5]
report = {"test_n": len(te), "accuracy": round(acc, 4), "macro_f1": round(mf1, 4),
          "infer_ms_per_sample_cpu": round(infer_ms, 2),
          "worst_5_classes": worst,
          "gate_acc_90": acc >= 0.90, "gate_f1_90": mf1 >= 0.90}
(EXP / "test_report.json").write_text(json.dumps(report, indent=1))
print("test:", json.dumps(report))
