"""Task 2 — confidence calibration (temperature scaling) primitives.

Fits nowhere near thresholds: temperature is learned on VAL only by
scripts/calibrate_v4.py and shipped in models/<active>/calibration.json.
These tests pin the pure deps behavior: identity at T=1, flattening at T>1,
and batch/single-row equivalence of recognize_probs*.
"""
import numpy as np

from app import deps


def test_get_calibration_defaults_to_identity(monkeypatch, tmp_path):
    monkeypatch.setattr("app.deps._calibration_path", lambda: tmp_path / "missing.json")
    assert deps.get_calibration() == {"temperature": 1.0}


def test_calibrate_probs_identity_and_flattening(monkeypatch, tmp_path):
    p = np.array([0.8, 0.1, 0.1], dtype=np.float32)
    assert np.allclose(deps.calibrate_probs(p), p)
    monkeypatch.setattr(deps, "get_calibration", lambda: {"temperature": 2.0})
    q = deps.calibrate_probs(p)
    assert q.max() < 0.8
    assert np.isclose(q.sum(), 1.0)


def test_recognize_probs_batch_matches_single_rows():
    X = np.random.default_rng(0).normal(0, 0.5, (6, 45, 189)).astype("float32")
    batch = deps.recognize_probs_batch(X)
    rows = np.stack([deps.recognize_probs(x) for x in X])
    assert batch.shape == rows.shape
    assert np.allclose(batch.sum(axis=1), 1.0, atol=1e-5)
    # float32 batch-vs-single matmul differences are expected; 1e-4 still
    # pins that both paths run the same models + calibration.
    assert np.allclose(batch, rows, atol=1e-4), float(np.abs(batch - rows).max())


def test_recognize_probs_batch_rows_are_non_negative():
    X = np.random.default_rng(1).normal(0, 0.5, (4, 45, 189)).astype("float32")
    probs = deps.recognize_probs_batch(X)
    assert probs.shape == (4, 109)
    assert (probs >= 0.0).all()


def test_make_windows_contract():
    # TTA view set (Task 5): k in {1,3}, anything else falls back to 1.
    x = np.zeros((45, 189), dtype="float32")
    assert deps.make_windows(x, 1).shape == (1, 45, 189)
    w3 = deps.make_windows(x, 3)
    assert w3.shape == (3, 45, 189)
    assert np.isfinite(w3).all()
    for k in (0, 2, 4, -1):
        assert deps.make_windows(x, k).shape == (1, 45, 189)


def test_live_policy_tta_windows_supported():
    pol = deps.get_policy()
    assert int(pol.get("tta_windows", 1)) in (1, 3)
