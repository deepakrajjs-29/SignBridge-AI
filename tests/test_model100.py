"""Task 6: Softmax(100) output shape (RED first, then GREEN)."""

import json
from pathlib import Path

from ai.models.lstm import NCLASS, build_gru, build_lstm

EVAL = Path(__file__).resolve().parents[1] / "models" / "SBAI-MDL-ISL-2.0.0" / "eval.json"


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


def test_eval_gates_90():
    gate = json.loads(EVAL.read_text(encoding="utf-8"))
    assert gate["accuracy"] >= 0.90
    assert gate["macro_f1"] >= 0.90
    assert gate["latency_p95_ms"] < 200
    assert gate["fps"] >= 15
