"""T3.4 — register winner (GRU), export SavedModel, parity check, registry."""
import hashlib, json, shutil, sys
from pathlib import Path
import numpy as np

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
import tensorflow as tf

WIN_EXP = ROOT / "models" / "EXP-2026-001-gru-full"
WIN_FILE = WIN_EXP / "SBAI-MDL-ISL-1.0.0_gru.keras"
FINAL = ROOT / "models" / "SBAI-MDL-ISL-1.0.0.keras"
EXPORT = ROOT / "models" / "SBAI-MDL-ISL-1.0.0_savedmodel"
shutil.copyfile(WIN_FILE, FINAL)

model = tf.keras.models.load_model(FINAL)
model.export(str(EXPORT))

# parity: keras vs exported SavedModel on 200-sample probe
D = np.load(ROOT / "data/dataset/processed/tensors_mvp50.npz")
S = np.load(ROOT / "data/dataset/processed/split_idx.npz")
SC = np.load(ROOT / "models/scaler_mvp50.npz")
Xs = ((D["X"].astype("float32") - SC["mean"]) / SC["std"]).astype("float32")
probe = Xs[S["test"][:200]]
p1 = model.predict(probe, verbose=0).argmax(1)
loaded = tf.saved_model.load(str(EXPORT))
infer = loaded.signatures["serving_default"]
p2 = infer(tf.constant(probe))["output_0"].numpy().argmax(1)
parity = bool((p1 == p2).all())

sha = hashlib.sha256(FINAL.read_bytes()).hexdigest()
test_rep = json.loads((WIN_EXP / "test_report.json").read_text())
policy = json.loads((WIN_EXP / "policy.json").read_text())
registry = {
    "model_id": "SBAI-MDL-ISL-1.0.0", "arch": "GRU128-GRU64-Dense64-Softmax50",
    "status": "Candidate (M3 gate debt: test 0.824/0.823 below 0.90 gates)",
    "seq_len": 45, "feat_dim": 189, "classes": 50,
    "sha256": sha, "export_parity_200": parity,
    "test": test_rep, "policy": policy,
    "challenger_lstm": "test 0.773/0.764 — GRU promoted on evidence",
    "fixes": ["handedness canonicalization (U014 slot flip)", "mirror+scale+shift+noise+drop train aug"],
}
(ROOT / "models" / "registry.json").write_text(json.dumps(registry, indent=1))
print(json.dumps({"registered": FINAL.name, "sha256": sha[:16] + "…", "parity": parity,
                  "test_acc": test_rep["accuracy"], "test_f1": test_rep["macro_f1"]}))
