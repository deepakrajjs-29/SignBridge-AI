"""Motion-sensitivity probe transforms for eval scripts (numpy only, no TF)."""

from __future__ import annotations

import numpy as np


def staticify(X: np.ndarray) -> np.ndarray:
    """(n,T,F) -> (n,T,F) with every timestep replaced by frame 0."""
    return np.repeat(X[:, :1, :], X.shape[1], axis=1)


def time_shuffle(X: np.ndarray, seed: int = 7) -> np.ndarray:
    """(n,T,F) -> (n,T,F), per-sample timestep permutation, deterministic for seed."""
    rng = np.random.default_rng(seed)
    out = np.empty_like(X)
    for i in range(X.shape[0]):
        perm = rng.permutation(X.shape[1])
        out[i] = X[i, perm]
    return out
