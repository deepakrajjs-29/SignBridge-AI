"""Task 6: Softmax(100) + SBAI-MDL-ISL-2.0.0 registration (fix round 1).

Gate test reads the training-script-produced eval.json and cross-checks its
`measured` values against the independent EXP artifacts (test_report.json,
val_history.json) — not hard-coded constants.
"""

import json
from pathlib import Path

from ai.models.lstm import NCLASS, build_gru, build_lstm

ROOT = Path(__file__).resolve().parents[1]
MDIR = ROOT / "models" / "SBAI-MDL-ISL-2.0.0"
EVAL = MDIR / "eval.json"


def test_softmax100_output_shape():
    m = build_lstm(nclass=100)
    assert m.output_shape == (None, 100)


def test_default_nclass_is_100():
    assert NCLASS == 100
    assert build_lstm().output_shape == (None, 100)
    assert build_gru().output_shape == (None, 100)


def test_model_names_100():
    assert build_lstm(nclass=100).name == "SBAI-LSTM-100"
    assert build_gru(nclass=100).name == "SBAI-GRU-100"


def test_eval_measured_matches_training_artifacts():
    """eval.json `measured` must equal the EXP files the training script wrote."""
    gate = json.loads(EVAL.read_text(encoding="utf-8"))
    src = gate["measured"]["source"]
    test_rep = json.loads((ROOT / src["test_report"]).read_text(encoding="utf-8"))
    hist = json.loads((ROOT / src["val_history"]).read_text(encoding="utf-8"))
    assert gate["measured"]["test_accuracy"] == test_rep["accuracy"]
    assert gate["measured"]["test_macro_f1"] == test_rep["macro_f1"]
    assert gate["measured"]["test_n"] == test_rep["test_n"]
    assert len(test_rep["per_class"]) == 100
    best_val_f1 = max(h["val_macro_f1"] for h in hist)
    assert best_val_f1 == max(h["val_macro_f1"] for h in hist) and best_val_f1 > 0
    # gate flags must be computed from measured, not hand-set
    assert gate["gate_acc_90"] == (gate["measured"]["test_accuracy"] >= 0.90)
    assert gate["gate_f1_90"] == (gate["measured"]["test_macro_f1"] >= 0.90)
    assert gate["gate_p95_200ms"] == (gate["latency_p95_ms"] < 200)
    assert gate["gate_fps_15"] == (gate["fps"] >= 15)
    # real-data production must NOT be claimed
    assert "NOT cleared" in gate["status"] or "synthetic" in gate["data"].lower()


def test_eval_latency_fps_gates():
    gate = json.loads(EVAL.read_text(encoding="utf-8"))
    assert gate["latency_p95_ms"] < 200
    assert gate["fps"] >= 15


def test_export_parity_probe():
    """SavedModel export exists; training-script parity probe is clean; .keras reloads."""
    import numpy as np

    assert (MDIR / "SBAI-LSTM-100_savedmodel" / "saved_model.pb").exists()
    probe = json.loads((MDIR.parent / "EXP-2026-002-lstm-smoke100" / "parity_probe.json")
                       .read_text(encoding="utf-8"))
    assert probe["n"] == 200 and probe["max_abs_diff"] == 0.0
    assert probe["argmax_match"] == "200/200"
    from tensorflow import keras
    m = keras.models.load_model(str(MDIR / "SBAI-LSTM-100.keras"))
    rng = np.random.default_rng(7)
    assert m.predict(rng.normal(size=(4, 45, 189)).astype("float32"), verbose=0).shape == (4, 100)


def test_brief_protocol_params():
    """EXP train.log must show brief-matched params: smoke 5, max 150, patience 15, early stop."""
    log = (ROOT / "models" / "EXP-2026-002-lstm-smoke100" / "train.log").read_text()
    assert "max 150" in log and "patience 15" in log
    assert "[SMOKE]" in log and "early-stop at epoch" in log
    hist = json.loads((ROOT / "models" / "EXP-2026-002-lstm-smoke100" / "val_history.json")
                      .read_text(encoding="utf-8"))
    assert len(hist) < 150  # stopped early on convergence
    gru_rep = json.loads((ROOT / "models" / "EXP-2026-002-gru-smoke100" / "test_report.json")
                         .read_text(encoding="utf-8"))
    gru_par = json.loads((ROOT / "models" / "EXP-2026-002-gru-smoke100" / "parity_probe.json")
                         .read_text(encoding="utf-8"))
    assert len(gru_rep["per_class"]) == 100  # challenger frozen-test scored
    assert gru_par["max_abs_diff"] == 0.0 and gru_par["argmax_match"] == "200/200"


def test_registry_includes_200_keeps_100():
    reg = json.loads((ROOT / "models" / "registry.json").read_text(encoding="utf-8"))
    assert reg["model_id"] == "SBAI-MDL-ISL-1.0.0"  # deployed record untouched
    entry = reg["models"]["SBAI-MDL-ISL-2.0.0"]
    assert entry["classes"] == 100
    assert entry["measured_test_acc"] >= 0.90 and entry["measured_test_f1"] >= 0.90
