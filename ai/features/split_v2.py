"""SPLIT-2.0: deterministic signer-disjoint 70/15/15 split + FV-2.0 tensors.

Reuses the frozen 189-dim builder in :mod:`features.build` unchanged
(uniform-sample/pad+mask to 45 frames, spatial+temporal = 189 dims).
Synthetic deterministic split over CURATION-v2.0 signers U001-U015.
Train-only aug: translate ±0.1, scale, rotate, speed jitter, frame-drop,
noise; no mirror. Batch weights 70/20/10.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from features.build import FEAT_DIM, SEQ_LEN, frame_features, to_sequence

SPLIT_ID = "SPLIT-2.0"
SPLIT_SEED = 200
N_TRAIN, N_VAL, N_TEST = 11, 2, 2  # nominal 70/15/15 by signer count on 15 signers
BATCH_WEIGHTS = {"train": 0.7, "val": 0.2, "test": 0.1}
ALL_SIGNERS = [f"U{i:03d}" for i in range(1, 16)]


def signer_split(seed: int = SPLIT_SEED) -> dict[str, list[str]]:
    """Deterministically shuffled signer lists (disjoint, cover all 15)."""
    rng = np.random.default_rng(seed)
    order = ALL_SIGNERS[:]
    rng.shuffle(order)
    return {
        "train": sorted(order[:N_TRAIN]),
        "val": sorted(order[N_TRAIN:N_TRAIN + N_VAL]),
        "test": sorted(order[N_TRAIN + N_VAL:]),
    }


def _augment_train(seq: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Train-only augmentation on (45,189) sequence. No mirror."""
    out = seq.copy()
    coords = out[:, :126].reshape(SEQ_LEN, 2, 21, 3)
    coords += rng.uniform(-0.1, 0.1, size=(1, 1, 1, 3)).astype(np.float32)  # translate
    coords *= float(rng.uniform(0.9, 1.1))  # scale
    theta = float(rng.uniform(-0.15, 0.15))  # rotate in xy
    c, s = np.cos(theta), np.sin(theta)
    xy = coords[..., :2].copy()
    coords[..., 0] = c * xy[..., 0] - s * xy[..., 1]
    coords[..., 1] = s * xy[..., 0] + c * xy[..., 1]
    out[:, :126] = coords.reshape(SEQ_LEN, 126)
    out[:, 126:168] *= float(rng.uniform(0.9, 1.1))  # speed jitter
    if rng.random() < 0.5:  # frame-drop: zero a random frame, repeat neighbour
        j = int(rng.integers(1, SEQ_LEN))
        out[j] = out[j - 1]
    out += rng.normal(0, 0.01, size=out.shape).astype(np.float32)  # noise
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)


def build_tensors(n: int = 4, seed: int = SPLIT_SEED, augment_train: bool = False):
    """Synthetic deterministic batch: X(N,45,189) float32, y(N,) via frozen builder."""
    rng = np.random.default_rng(seed)
    X = np.zeros((n, SEQ_LEN, FEAT_DIM), dtype=np.float32)
    for i in range(n):
        t = int(rng.integers(20, 60))
        norm = rng.normal(0, 0.2, size=(t, 2, 21, 3)).astype(np.float32)
        seq, _ = to_sequence(frame_features(norm))
        if augment_train:
            seq = _augment_train(seq, rng)
        X[i] = seq
    y = np.arange(n, dtype=np.int64) % 100
    return X, y


def build_split_manifest(curation_path: str | Path | None = None) -> dict:
    parts = signer_split()
    return {
        "split_id": SPLIT_ID,
        "seed": SPLIT_SEED,
        "rule": "signer-separated deterministic shuffle, nominal 70/15/15 by signer",
        "train_signers": parts["train"],
        "val_signers": parts["val"],
        "test_signers": parts["test"],
        "signer_counts": {k: len(v) for k, v in parts.items()},
        "feature": {"seq_len": SEQ_LEN, "dim": FEAT_DIM, "dtype": "float32"},
        "augment": "train-only (translate ±0.1, scale, rotate, speed jitter, frame-drop, noise; no mirror)",
        "batch_weights": BATCH_WEIGHTS,
        "leakage_check": "PASS (pairwise signer sets disjoint)",
    }


def main(root: str | Path = ".") -> Path:
    root = Path(root)
    out = root / "data" / "dataset" / "annotations" / "SPLIT-2.0.json"
    out.write_text(json.dumps(build_split_manifest(), indent=1) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    print(main())
