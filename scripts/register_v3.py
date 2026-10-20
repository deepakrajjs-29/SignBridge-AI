"""V3+ register the REAL winner (defaults = 100-class 3.0.0; override
--exp/--model-id/--tag for later vocabs, e.g. 109-class 4.0.0).

Compares {exp} LSTM vs GRU frozen-test reports, promotes the winner
on evidence (higher macro_f1; tie -> LSTM primary), exports SavedModel,
checks 200-sample parity, and merges into models/registry.json preserving
deployment keys (active_model untouched — promotion is a separate step).
"""
import argparse
import csv
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
P.add_argument("--tag", default="100_real")
P.add_argument("--exp", default="EXP-2026-003")
P.add_argument("--model-id", default="SBAI-MDL-ISL-3.0.0")
A = P.parse_args()
SPLIT_TAG = A.tag.split("_")[0]

sys.path.insert(0, str(ROOT / "ai"))
import numpy as np
import tensorflow as tf

EXPS = {a: ROOT / "models" / f"{A.exp}-{a}-full" for a in ("lstm", "gru")}
reps = {a: json.loads((e / "test_report.json").read_text()) for a, e in EXPS.items()}
if A.pick == "auto":
    win = "lstm" if reps["lstm"]["macro_f1"] >= reps["gru"]["macro_f1"] else "gru"
else:
    win = A.pick
lose = "gru" if win == "lstm" else "lstm"
print(f"lstm {reps['lstm']['accuracy']}/{reps['lstm']['macro_f1']} vs "
      f"gru {reps['gru']['accuracy']}/{reps['gru']['macro_f1']} -> {win}", flush=True)

WIN_FILE = EXPS[win] / f"{A.model_id}_{win}.keras"
FINAL = ROOT / "models" / f"{A.model_id}.keras"
EXPORT = ROOT / "models" / f"{A.model_id}_savedmodel"
shutil.copyfile(WIN_FILE, FINAL)
# Ensemble serving needs BOTH arch weights beside the registry entry.
for a in ("lstm", "gru"):
    src = EXPS[a] / f"{A.model_id}_{a}.keras"
    if src.exists():
        shutil.copyfile(src, ROOT / "models" / f"{A.model_id}_{a}.keras")

model = tf.keras.models.load_model(FINAL)
model.export(str(EXPORT))

D = np.load(ROOT / "data/dataset/processed" / f"tensors_{A.tag}.npz")
S = np.load(ROOT / "data/dataset/processed" / f"split_idx_{SPLIT_TAG}.npz")
SC = np.load(ROOT / "models" / f"scaler_{SPLIT_TAG}_real.npz")
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
MDIR = ROOT / "models" / A.model_id
MDIR.mkdir(parents=True, exist_ok=True)
(MDIR / "policy.json").write_text(json.dumps(policy, indent=1))
NCLASS = len(list(csv.DictReader(
    (ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8"))))
arch_tpl = "LSTM128-LSTM64-Dense64-Softmax{n}" if win == "lstm" else "GRU128-GRU64-Dense64-Softmax{n}"
arch = arch_tpl.format(n=NCLASS)
fresh = {
    "model_id": A.model_id, "arch": arch,
    "status": f"Candidate (real-data {NCLASS}-class; awaiting gate sign-off)",
    "seq_len": 45, "feat_dim": 189, "classes": NCLASS,
    "sha256": sha, "export_parity_200": parity,
    "test": test_rep, "policy": policy,
    "challenger": f"{lose} test {reps[lose]['accuracy']}/{reps[lose]['macro_f1']}",
    "data": f"CURATION-v{4 if NCLASS > 100 else 3}.0 (ISL500 real landmarks, signer-separated SPLIT)",
}
fresh_models = {
    A.model_id: {
        "arch": arch, "classes": NCLASS, "sha256_lstm": sha,
        "measured_test_acc": test_rep["accuracy"],
        "measured_test_f1": test_rep["macro_f1"],
        "eval": f"{A.exp} frozen test",
    }
}
reg_path = ROOT / "models" / "registry.json"
try:
    existing = json.loads(reg_path.read_text())
except (FileNotFoundError, json.JSONDecodeError):
    existing = {}
registry = build_registry(existing, fresh)
models_tbl = registry.get("models")
# Merge, never overwrite: prior entries (e.g. 2.0.0/3.0.0) must survive.
# NOTE: registry comes from `fresh` (which carries no "models" key), so the
# merge base must always be existing.get("models"), not registry.get("models").
merged_tbl = dict(existing.get("models", {})) if isinstance(existing.get("models"), dict) else {}
if isinstance(models_tbl, dict):
    merged_tbl.update(models_tbl)
merged_tbl.update(fresh_models)
registry["models"] = merged_tbl
reg_path.write_text(json.dumps(registry, indent=1))
print(json.dumps({"registered": FINAL.name, "winner": win, "sha256": sha[:16] + "...",
                  "parity": parity, "test_acc": test_rep["accuracy"],
                  "test_f1": test_rep["macro_f1"]}), flush=True)
