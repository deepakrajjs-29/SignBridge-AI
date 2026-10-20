"""Motion-sensitivity probes on the frozen TEST split (active ensemble, v1 features).

Answers: does the deployed sequence model use temporal order, and how much does
destroying motion (staticify) or scrambling order (time_shuffle) cost accuracy?

Conditions (all on scaled (n,45,189) test tensors):
  full          identity — must reproduce frozen TEST argmax (~0.8129) as sanity
  staticify     every timestep replaced by frame 0 (shape-only input)
  time_shuffle  per-sample timestep permutation, seed=7 (order destroyed, multiset kept)

Usage: py -3 scripts/eval_motion_sensitivity.py
Writes: Docs/eval/motion_sensitivity.json
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "backend"))
from app import deps  # noqa: E402
from app.eval_probe import staticify, time_shuffle  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402

FROZEN_TEST_ACC = 0.8129
SANITY_TOL = 0.005

D = np.load(ROOT / "data/dataset/processed" / "tensors_109_real.npz")
S = np.load(ROOT / "data/dataset/processed" / "split_idx_109.npz")
SC = np.load(ROOT / "models" / "scaler_109_real.npz")

X = D["X"].astype("float32")[S["test"]]
y = D["y"][S["test"]]
Xs = ((X - SC["mean"]) / SC["std"]).astype("float32")

conditions = {
    "full": Xs,
    "staticify": staticify(Xs),
    "time_shuffle": time_shuffle(Xs, seed=7),
}

results = {}
for name, Xc in conditions.items():
    t0 = time.perf_counter()
    probs = deps.recognize_probs_batch(Xc)
    pred = probs.argmax(1)
    acc = float((pred == y).mean())
    f1 = float(f1_score(y, pred, average="macro", zero_division=0))
    results[name] = {
        "argmax_acc": round(acc, 4),
        "macro_f1": round(f1, 4),
        "seconds": round(time.perf_counter() - t0, 1),
    }
    print(f"{name:12s} argmax_acc={acc:.4f} macro_f1={f1:.4f}", flush=True)

sanity = abs(results["full"]["argmax_acc"] - FROZEN_TEST_ACC) <= SANITY_TOL
report = {
    "model_version": deps.model_version(),
    "n_test": int(len(y)),
    "generated": time.strftime("%Y-%m-%d"),
    "frozen_test_acc_ref": FROZEN_TEST_ACC,
    "sanity_full_within_0.005": bool(sanity),
    "conditions": results,
}
out = ROOT / "Docs" / "eval" / "motion_sensitivity.json"
out.write_text(json.dumps(report, indent=2))
print(f"sanity(full vs {FROZEN_TEST_ACC}): {'PASS' if sanity else 'FAIL'}")
print(f"wrote {out}")
if not sanity:
    sys.exit(1)
