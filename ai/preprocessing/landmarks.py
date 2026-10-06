"""Landmark loading + validation + wrist-relative normalization (T2.2/T2.3)."""

from __future__ import annotations

import h5py
import numpy as np

HANDS, JPTS, DIMS = 2, 21, 3
WRIST = 0


def load_h5(path: str) -> np.ndarray:
    """Return (T,2,21,3) float32. Raises on bad file."""
    with h5py.File(path, "r") as f:
        if "intermediate" not in f:
            raise ValueError(f"no 'intermediate' dataset in {path}")
        arr = np.asarray(f["intermediate"], dtype=np.float32)
    if arr.ndim != 4 or arr.shape[1:] != (HANDS, JPTS, DIMS):
        raise ValueError(f"unexpected shape {arr.shape} in {path}")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"NaN/Inf in {path}")
    return arr


def hand_present(hand: np.ndarray) -> bool:
    return bool(np.any(hand != 0))


def canonicalize(frames: np.ndarray) -> np.ndarray:
    """Dominant-hand-first slot order (handedness-invariant representation).

    MediaPipe slot order follows image-side detection, so a left-handed
    signer lands in slot 0 while right-handed signers land in slot 1
    (observed: U014 vs all others). Sorting slots by per-sequence activity
    makes train/inference features signer-invariant. Deterministic.
    """
    act = np.array([np.count_nonzero(frames[:, h]) for h in range(HANDS)])
    if act[1] > act[0]:
        return frames
    return frames[:, ::-1, :, :]


def normalize(frames: np.ndarray) -> np.ndarray:
    """Wrist-relative, hand-size scaled. (T,2,21,3). Missing hand stays zero."""
    out = np.zeros_like(frames)
    for t in range(frames.shape[0]):
        for h in range(HANDS):
            hand = frames[t, h]
            if not hand_present(hand):
                continue
            ref = hand[WRIST].copy()
            shifted = hand - ref
            scale = float(np.max(np.linalg.norm(shifted, axis=1)))
            out[t, h] = shifted / scale if scale > 1e-6 else shifted
    return out
