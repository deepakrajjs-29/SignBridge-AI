"""Task 5: FV-2.0 / SPLIT-2.0 — signer-disjoint split + (N,45,189) tensors."""

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "data" / "dataset" / "annotations" / "SPLIT-2.0.json"


def load_json(path=SPLIT):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tensor_shape(name="X"):
    """Build a small synthetic batch through the frozen 189-dim builder."""
    import sys

    sys.path.insert(0, str(ROOT / "ai"))
    from features.build import SEQ_LEN, FEAT_DIM, frame_features, to_sequence
    from features.split_v2 import build_tensors

    assert SEQ_LEN == 45 and FEAT_DIM == 189
    X, _ = build_tensors(n=4, seed=200)
    assert X.dtype == np.float32
    # cross-check single-sample path through frame_features + to_sequence
    rng = np.random.default_rng(200)
    norm = rng.normal(0, 0.2, size=(30, 2, 21, 3)).astype(np.float32)
    seq, mask = to_sequence(frame_features(norm))
    assert seq.shape == (45, 189) and mask.shape == (45,)
    return (None,) + tuple(X.shape[1:]) if name == "X" else tuple(X.shape)


def test_split_v2_signer_disjoint_and_shape():
    s = load_json("data/dataset/annotations/SPLIT-2.0.json")
    assert set(s["train_signers"]) & set(s["test_signers"]) == set()
    assert set(s["train_signers"]) & set(s["val_signers"]) == set()
    assert set(s["val_signers"]) & set(s["test_signers"]) == set()
    assert tensor_shape("X") == (None, 45, 189)


def test_split_v2_ratios_nominal_70_15_15():
    s = load_json("data/dataset/annotations/SPLIT-2.0.json")
    n = len(s["train_signers"]) + len(s["val_signers"]) + len(s["test_signers"])
    assert n == 15  # U001-U015 from CURATION-v2.0
    assert s["split_id"] == "SPLIT-2.0"
    # nominal 70/15/15 by signer count, allowing integer rounding on 15 signers
    assert len(s["train_signers"]) in (10, 11)
    assert len(s["val_signers"]) in (2, 3)
    assert len(s["test_signers"]) in (2, 3)
