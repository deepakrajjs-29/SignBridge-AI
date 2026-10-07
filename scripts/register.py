"""T3.4 — register winner (GRU), export SavedModel, parity check, registry."""
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Registry keys owned by the deploy/promote flow — a training re-registration
# must never drop them (that would silently un-promote prod).
DEPLOYMENT_KEYS = ("active_model", "previous_model", "history")


def build_registry(existing: dict, fresh: dict | None = None) -> dict:
    """Merge a fresh training registry over an existing one, preserving deploys.

    Pure: no file IO and neither input is mutated. ``existing`` is the current
    registry (e.g. read from models/registry.json, ``{}`` when absent);
    ``fresh`` is the newly computed training registry. Training keys come from
    ``fresh``; the deployment keys (``active_model``/``previous_model``/
    ``history``) are carried over from ``existing`` when present and never
    invented. When ``fresh`` is omitted the training keys carry over too.
    """
    base = existing if fresh is None else fresh
    merged = copy.deepcopy(base)
    if fresh is not None:
        for key in DEPLOYMENT_KEYS:
            if key in existing:
                merged[key] = copy.deepcopy(existing[key])
    return merged


def main() -> None:
    sys.path.insert(0, str(ROOT / "ai"))
    import numpy as np
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
    fresh = {
        "model_id": "SBAI-MDL-ISL-1.0.0", "arch": "GRU128-GRU64-Dense64-Softmax50",
        "status": "Candidate (M3 gate debt: test 0.824/0.823 below 0.90 gates)",
        "seq_len": 45, "feat_dim": 189, "classes": 50,
        "sha256": sha, "export_parity_200": parity,
        "test": test_rep, "policy": policy,
        "challenger_lstm": "test 0.773/0.764 — GRU promoted on evidence",
        "fixes": ["handedness canonicalization (U014 slot flip)", "mirror+scale+shift+noise+drop train aug"],
    }
    reg_path = ROOT / "models" / "registry.json"
    try:
        existing = json.loads(reg_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}
    registry = build_registry(existing, fresh)
    reg_path.write_text(json.dumps(registry, indent=1))
    print(json.dumps({"registered": FINAL.name, "sha256": sha[:16] + "…", "parity": parity,
                      "test_acc": test_rep["accuracy"], "test_f1": test_rep["macro_f1"]}))


if __name__ == "__main__":
    main()
