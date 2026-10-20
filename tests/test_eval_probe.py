import numpy as np

from app.eval_probe import staticify, time_shuffle


def _mk(n=3, t=45, f=8, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, t, f)).astype(np.float32)


def test_staticify_replaces_all_steps_with_frame0():
    X = _mk()
    S = staticify(X)
    assert S.shape == X.shape
    for t in range(X.shape[1]):
        np.testing.assert_array_equal(S[:, t, :], X[:, 0, :])


def test_time_shuffle_deterministic():
    X = _mk(n=5, seed=1)
    a = time_shuffle(X, seed=7)
    b = time_shuffle(X, seed=7)
    np.testing.assert_array_equal(a, b)
    c = time_shuffle(X, seed=8)
    assert not np.array_equal(a, c)


def test_time_shuffle_preserves_row_multiset():
    X = _mk(n=4, seed=2)
    S = time_shuffle(X, seed=7)
    for i in range(X.shape[0]):
        orig = sorted(map(tuple, X[i].tolist()))
        got = sorted(map(tuple, S[i].tolist()))
        assert orig == got


def test_time_shuffle_actually_shuffles():
    ramp = np.arange(45, dtype=np.float32)[None, :, None]
    X = np.repeat(ramp, 6, axis=2)
    S = time_shuffle(X, seed=7)
    assert not np.array_equal(S, X)
    assert sorted(S[0, :, 0].tolist()) == list(range(45))
