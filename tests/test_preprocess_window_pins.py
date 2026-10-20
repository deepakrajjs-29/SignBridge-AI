"""Characterization pins for backend.app.deps.preprocess_window (P2).

Documents CURRENT behavior: repeat-pad below SEQ_LEN (pad row = last input
row), linspace resample at/above SEQ_LEN, pre-normalization No-Sign energy
gate. If any of these fail, the implementation drifted — investigate before
changing tests (they pin shipped serving behavior, not an ideal).
"""
import numpy as np

from app import deps


def test_pad_below_seq_len_repeats_last_input_row():
    t = 30
    frames = np.full((t, 189), 5.0, dtype=np.float32)
    out = deps.preprocess_window(frames)
    assert out is not None
    assert out.shape == (45, 189)
    # rows 30..44 are the scaled copy of the last input row (index 29)
    np.testing.assert_allclose(
        out[30:45], np.repeat(out[29][None, :], 15, axis=0), rtol=1e-6, atol=1e-6
    )


def test_linspace_resample_matches_reference_indices_on_ramp():
    t = 100
    ramp = np.repeat(np.arange(t, dtype=np.float32)[:, None], 189, axis=1)
    out = deps.preprocess_window(ramp)
    assert out is not None
    assert out.shape == (45, 189)
    idx = np.linspace(0, t - 1, 45).astype(int)
    assert (np.diff(idx) >= 0).all()  # monotone (linspace order property)
    mu, sd = deps.get_scaler()
    expected = (idx.astype(np.float32)[:, None] - mu.reshape(1, -1)) / sd.reshape(1, -1)
    np.testing.assert_allclose(out, expected.astype(np.float32), rtol=1e-4, atol=1e-4)


def test_all_zero_input_triggers_energy_gate_returns_none():
    # No-Sign indication is a None return (both a full and a short clip).
    assert deps.preprocess_window(np.zeros((45, 189), dtype=np.float32)) is None
    assert deps.preprocess_window(np.zeros((30, 189), dtype=np.float32)) is None
