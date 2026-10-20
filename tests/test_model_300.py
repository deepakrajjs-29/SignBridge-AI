"""3.0.0 wiring gate: version-aware artifact paths must resolve to the
REAL 100-class artifacts (not silently fall back to 1.0.0/2.0.0 files)."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import deps


def test_paths_resolve_to_300_artifacts(monkeypatch):
    monkeypatch.setattr(deps, "model_version", lambda: "SBAI-MDL-ISL-3.0.0")
    assert deps._active_keras_path().name == "SBAI-MDL-ISL-3.0.0.keras"
    assert deps._active_scaler_path().name == "scaler_100_real.npz"
    assert deps._policy_path().parent.name == "SBAI-MDL-ISL-3.0.0"
    assert deps.uses_ensemble() is True


def test_paths_resolve_to_400_artifacts(monkeypatch):
    monkeypatch.setattr(deps, "model_version", lambda: "SBAI-MDL-ISL-4.0.0")
    assert deps._active_keras_path().name == "SBAI-MDL-ISL-4.0.0.keras"
    assert deps._active_scaler_path().name == "scaler_109_real.npz"
    assert deps._policy_path().parent.name == "SBAI-MDL-ISL-4.0.0"
    assert deps.uses_ensemble() is True


def test_legacy_paths_unchanged(monkeypatch):
    monkeypatch.setattr(deps, "model_version", lambda: "SBAI-MDL-ISL-2.0.0")
    assert deps._active_keras_path().name == "SBAI-LSTM-100.keras"
    monkeypatch.setattr(deps, "model_version", lambda: "SBAI-MDL-ISL-1.0.0")
    assert deps._active_keras_path().name == "SBAI-MDL-ISL-1.0.0.keras"


def test_infer_ensemble_is_probability_distribution():
    X = np.random.default_rng(3).normal(0, 0.5, (2, 45, 189)).astype("float32")
    probs = deps.infer_ensemble(X)
    assert probs.shape == (2, 109)
    assert np.all(probs >= 0.0)
    assert np.allclose(probs.sum(axis=1), 1.0, atol=1e-5)
