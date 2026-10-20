"""Ensemble serving gate: 4.0.0 inference = mean(LSTM, GRU, mirror-TTA).

- mirror_features is an involution and matches training augmentation.
- infer_ensemble returns (1,109) probs summing to 1.
- Frozen-test numbers pinned to measured ensemble values (n=3629).
  3.0.0 values (0.8109/0.8062, n=3326) live in git history + Docs/M10_GATE_100REAL.md.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import deps


def test_mirror_is_involution_and_training_identical():
    rng = np.random.default_rng(7)
    x = rng.normal(0, 0.5, (2, 45, 189)).astype("float32")
    back = deps.mirror_features(deps.mirror_features(x))
    assert np.allclose(back, x, atol=1e-6)
    # x-coords negated, speeds/magnitudes untouched
    m = deps.mirror_features(x)
    assert np.allclose(m[:, :, :126].reshape(-1, 45, 2, 21, 3)[..., 0],
                       -x[:, :, :126].reshape(-1, 45, 2, 21, 3)[..., 0], atol=1e-6)
    assert np.allclose(m[:, :, 126:168], x[:, :, 126:168], atol=1e-6)


def test_ensemble_proba_shape_and_mass():
    probs = deps.infer_ensemble(np.zeros((1, 45, 189), dtype="float32"))
    assert probs.shape == (1, 109)
    assert abs(float(probs.sum()) - 1.0) < 1e-4


def test_ensemble_frozen_numbers():
    from sklearn.metrics import accuracy_score, f1_score

    D = np.load(ROOT / "data/dataset/processed/tensors_109_real.npz")
    S = np.load(ROOT / "data/dataset/processed/split_idx_109.npz")
    mu, sd = deps.get_scaler()
    Xs = ((D["X"].astype("float32") - mu) / sd).astype("float32")
    te = S["test"]
    yp = deps.infer_ensemble(Xs[te]).argmax(1)
    assert round(float(accuracy_score(D["y"][te], yp)), 4) == 0.8129
    assert round(float(f1_score(D["y"][te], yp, average="macro", zero_division=0)), 4) == 0.8079
