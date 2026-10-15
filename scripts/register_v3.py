"""V3 — register the REAL 100-class winner as SBAI-MDL-ISL-3.0.0.

Compares EXP-2026-003 LSTM vs GRU frozen-test reports, promotes the winner
on evidence (higher macro_f1; tie -> LSTM primary), exports SavedModel,
checks 200-sample parity, and merges into models/registry.json preserving
deployment keys (active_model untouched — promotion is a separate step).
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "scripts"))
from register import build_registry

P = argparse.ArgumentParser()
P.add_argument("--pick", choices=["auto", "lstm", "gru"], default="auto")
A = P.parse_args()

sys.path.insert(0, str(ROOT / "ai"))
import numpy as np
import tensorflow as tf

EXPS = {a: ROOT / "models" / f"EXP-2026-003-{a}-full" for a in ("lstm", "gru")}
reps = {a: json.loads((e / "test_report.json").read_text()) for a, e in EXPS.items()}
if A.pick == "auto":
    win = "lstm" if reps["lstm"]["macro_f1"] >= reps["gru"]["macro_f1"] else "gru"
else:
    win = A.pick
lose = "gru" if win == "lstm" else "lstm"
print(f"lstm {reps['lstm']['accuracy']}/{reps['lstm']['macro_f1']} vs "
      f"gru {reps['gru']['accuracy']}/{reps['gru']['macro_f1']} -> {win}", flush=True)

WIN_FILE = EXPS[win] / f"SBAI-MDL-ISL-3.0.0_{win}.keras"
FINAL = ROOT / "models" / "SBAI-MDL-ISL-3.0.0.keras"
EXPORT = ROOT / "models" / "SBAI-MDL-ISL-3.0.0_savedmodel"
shutil.copyfile(WIN_FILE, FINAL)

model = tf.keras.models.load_model(FINAL)
model.export(str(EXPORT))

D = np.load(ROOT / "data/dataset/processed/tensors_100_real.npz")
S = np.load(ROOT / "data/dataset/processed/split_idx_100.npz")
SC = np.load(ROOT / "models/scaler_100_real.npz")
Xs = ((D["X"].astype("float32") - SC["mean"]) / SC["std"]).astype("float32")
probe = Xs[S["test"][:200]]
p1 = model.predict(probe, verbose=0).argmax(1)
loaded = tf.saved_model.load(str(EXPORT))
infer = loaded.signatures["serving_default"]
p2 = infer(tf.constant(probe))["output_0"].numpy().argmax(1)
parity = bool((p1 == p2).all())

sha = hashlib.sha256(FINAL.read_bytes()).hexdigest()
test_rep = reps[win]
policy = json.loads((EXPS[win] / "policy.json").read_text())
MDIR = ROOT / "models" / "SBAI-MDL-ISL-3.0.0"
MDIR.mkdir(parents=True, exist_ok=True)
(MDIR / "policy.json").write_text(json.dumps(policy, indent=1))
arch = "LSTM128-LSTM64-Dense64-Softmax100" if win == "lstm" else "GRU128-GRU64-Dense64-Softmax100"
fresh = {
    "model_id": "SBAI-MDL-ISL-3.0.0", "arch": arch,
    "status": "Candidate (real-data 100-class; awaiting gate sign-off)",
    "seq_len": 45, "feat_dim": 189, "classes": 100,
    "sha256": sha, "export_parity_200": parity,
    "test": test_rep, "policy": policy,
    "challenger": f"{lose} test {reps[lose]['accuracy']}/{reps[lose]['macro_f1']}",
    "data": "CURATION-v3.0 (ISL500 real landmarks, signer-separated SPLIT-3.0)",
}
fresh_models = {
    "SBAI-MDL-ISL-3.0.0": {
        "arch": arch, "classes": 100, "sha256_lstm": sha,
        "measured_test_acc": test_rep["accuracy"],
        "measured_test_f1": test_rep["macro_f1"],
        "eval": "EXP-2026-003 frozen test",
    }
}
reg_path = ROOT / "models" / "registry.json"
try:
    existing = json.loads(reg_path.read_text())
except (FileNotFoundError, json.JSONDecodeError):
    existing = {}
registry = build_registry(existing, fresh)
models_tbl = registry.get("models")
if isinstance(models_tbl, dict):
    # Merge, never overwrite: prior entries (e.g. 2.0.0) must survive.
    merged_tbl = dict(existing.get("models", {})) if isinstance(existing.get("models"), dict) else {}
    merged_tbl.update(fresh_models)
    registry["models"] = merged_tbl
else:
    registry["models"] = dict(fresh_models)
reg_path.write_text(json.dumps(registry, indent=1))
print(json.dumps({"registered": FINAL.name, "winner": win, "sha256": sha[:16] + "...",
                  "parity": parity, "test_acc": test_rep["accuracy"],
                  "test_f1": test_rep["macro_f1"]}), flush=True)
