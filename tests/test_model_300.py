"""3.0.0 wiring gate: version-aware artifact paths must resolve to the
REAL 100-class artifacts (not silently fall back to 1.0.0/2.0.0 files)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import deps


def test_paths_resolve_to_300_artifacts(monkeypatch):
    monkeypatch.setattr(deps, "model_version", lambda: "SBAI-MDL-ISL-3.0.0")
    assert deps._active_keras_path().name == "SBAI-MDL-ISL-3.0.0.keras"
    assert deps._active_scaler_path().name == "scaler_100_real.npz"
    assert deps._policy_path().parent.name == "SBAI-MDL-ISL-3.0.0"


def test_legacy_paths_unchanged(monkeypatch):
    monkeypatch.setattr(deps, "model_version", lambda: "SBAI-MDL-ISL-2.0.0")
    assert deps._active_keras_path().name == "SBAI-LSTM-100.keras"
    monkeypatch.setattr(deps, "model_version", lambda: "SBAI-MDL-ISL-1.0.0")
    assert deps._active_keras_path().name == "SBAI-MDL-ISL-1.0.0.keras"
