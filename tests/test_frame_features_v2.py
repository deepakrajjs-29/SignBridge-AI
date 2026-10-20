"""Feature v2 (193-dim): 189 v1 rows + 4 global wrist trajectory channels."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ai"))

from features.build import (  # noqa: E402
    FEAT_DIM,
    FEAT_DIM_V2,
    frame_features,
    frame_features_v2,
)
from preprocessing.landmarks import canonicalize, normalize  # noqa: E402

T = 10


def _mk_frames():
    rng = np.random.default_rng(5)
    f = rng.normal(0, 0.2, size=(T, 2, 21, 3)).astype(np.float32)
    return f


def test_v2_shape_and_v1_prefix():
    f = _mk_frames()
    canon = canonicalize(f)
    norm = normalize(canon)
    X2 = frame_features_v2(canon, norm)
    assert FEAT_DIM_V2 == 193 and FEAT_DIM == 189
    assert X2.shape == (T, 193)
    np.testing.assert_array_equal(X2[:, :189], frame_features(norm))


def test_v2_trajectory_matches_wrist():
    T = 6
    f = np.zeros((T, 2, 21, 3), dtype=np.float32)
    for t in range(T):
        u = 0.1 + 0.05 * t
        f[t, 0, 0] = [u, 0.2, 0.0]
        for j in range(1, 21):
            f[t, 0, j] = [u + 0.01 * j, 0.3, 0.0]
    norm = normalize(f)
    X2 = frame_features_v2(f, norm)
    traj = X2[:, 189:]
    np.testing.assert_allclose(traj[:, 0], 0.1 + 0.05 * np.arange(T), atol=1e-6)
    np.testing.assert_allclose(traj[:, 1], 0.2, atol=1e-6)
    np.testing.assert_allclose(traj[0, 2:4], [0.0, 0.0], atol=1e-6)
    np.testing.assert_allclose(traj[1:, 2], 0.05, atol=1e-6)
    np.testing.assert_allclose(traj[1:, 3], 0.0, atol=1e-6)


def test_v2_missing_hand_zeros():
    T = 4
    f = np.zeros((T, 2, 21, 3), dtype=np.float32)
    for t in range(T):
        f[t, 0, 0] = [0.3, 0.4, 0.0]
        f[t, 0, 1:] = [0.31, 0.41, 0.0]
    f[2, 0] = 0.0  # hand 0 missing entirely in frame 2
    norm = normalize(f)
    X2 = frame_features_v2(f, norm)
    traj = X2[:, 189:]
    assert np.all(traj[2] == 0)
    assert np.all(traj[3, 2:4] == 0)  # delta across a missing frame suppressed
