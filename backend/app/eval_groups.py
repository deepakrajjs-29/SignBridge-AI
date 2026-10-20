"""Per-class motion-energy grouping (fix plan Task 11, P2).

Splits the 109 classes into low/mid/high temporal-motion groups from the
training-time speed channels (v1 layout: speeds at 126:168), so TEST F1 can
be compared across motion regimes (static-vs-dynamic follow-up).
"""
import numpy as np

# v1 feature layout: velocity channels occupy [126, 168)
SPEED_SLICE = slice(126, 168)


def class_motion_energy(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Per-class median over samples of mean |speed-channel| values.

    x: (n, T, F) features (raw or scaled — relative ordering per class is
    what grouping uses), y: (n,) integer class indices.
    Returns (C,) ordered by class index; classes absent from y are NaN.
    """
    y = np.asarray(y)
    n_classes = int(np.max(y)) + 1
    sample_energy = np.abs(np.asarray(x)[:, :, SPEED_SLICE]).mean(axis=(1, 2))
    out = np.full(n_classes, np.nan, dtype=np.float64)
    for c in range(n_classes):
        mask = y == c
        if np.any(mask):
            out[c] = float(np.median(sample_energy[mask]))
    return out


def assign_groups(energy: np.ndarray, n_groups: int = 3) -> np.ndarray:
    """Quantile groups: 0=low, 1=mid, 2=high motion (ties -> lower group)."""
    energy = np.asarray(energy, dtype=np.float64)
    if n_groups < 2:
        return np.zeros(energy.shape, dtype=int)
    bounds = np.quantile(energy, np.arange(1, n_groups) / n_groups)
    return np.searchsorted(bounds, energy, side="left").astype(int)
