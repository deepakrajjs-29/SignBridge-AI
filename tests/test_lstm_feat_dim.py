import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))

keras = pytest.importorskip("tensorflow.keras", reason="TF not available")

from models.lstm import build_gru, build_lstm  # noqa: E402


def test_build_lstm_default_feat_dim_189():
    m = build_lstm(nclass=109)
    assert m.input_shape == (None, 45, 189)


def test_build_lstm_feat_dim_193():
    m = build_lstm(nclass=109, feat_dim=193)
    assert m.input_shape == (None, 45, 193)


def test_build_gru_feat_dim_193():
    m = build_gru(nclass=109, feat_dim=193)
    assert m.input_shape == (None, 45, 193)
    assert build_gru().input_shape == (None, 45, 189)
