"""Frame features: 189 = 126 norm xyz + 42 speed magnitudes + 21 hand-shape stats (T2.3)."""

from __future__ import annotations

import numpy as np

from preprocessing.landmarks import DIMS, HANDS, JPTS, hand_present

SEQ_LEN, FEAT_DIM = 45, 189


def frame_features(norm: np.ndarray) -> np.ndarray:
    """norm (T,2,21,3) -> (T,189). Deterministic; zeros for missing hands."""
    t = norm.shape[0]
    coords = norm.reshape(t, HANDS * JPTS * DIMS)
    # speed magnitude per landmark vs previous frame (0 at t=0)
    speed = np.zeros((t, HANDS * JPTS), dtype=np.float32)
    diff = np.diff(norm, axis=0)
    speed[1:] = np.linalg.norm(diff, axis=3).reshape(t - 1, HANDS * JPTS)
    # per-hand bbox stats: min(3)+max(3)+center(3)+size(1) = 10/hand -> 20, +1 hand-count
    stats = np.zeros((t, 21), dtype=np.float32)
    for i in range(t):
        n = 0
        for h in range(HANDS):
            hand = norm[i, h]
            if not hand_present(hand):
                continue
            n += 1
            mn, mx = hand.min(0), hand.max(0)
            stats[i, h * 10:h * 10 + 3] = mn
            stats[i, h * 10 + 3:h * 10 + 6] = mx
            stats[i, h * 10 + 6:h * 10 + 9] = (mn + mx) / 2
            stats[i, h * 10 + 9] = float(np.linalg.norm(mx - mn))
        stats[i, 20] = n / 2.0
    feats = np.concatenate([coords, speed, stats], axis=1)
    assert feats.shape[1] == FEAT_DIM, feats.shape
    return np.nan_to_num(feats, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)


def to_sequence(feats: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(T,189) -> (45,189) + mask(45,). Uniform-sample if long, repeat-pad if short."""
    t = feats.shape[0]
    if t >= SEQ_LEN:
        idx = np.linspace(0, t - 1, SEQ_LEN).astype(int)
        return feats[idx], np.ones(SEQ_LEN, dtype=np.float32)
    pad = np.tile(feats[-1:], (SEQ_LEN - t, 1))
    return np.concatenate([feats, pad]), np.concatenate(
        [np.ones(t, dtype=np.float32), np.zeros(SEQ_LEN - t, dtype=np.float32)])
