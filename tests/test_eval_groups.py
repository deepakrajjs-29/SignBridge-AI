"""Tests for motion-energy grouping (fix plan Task 11)."""
import numpy as np

from app.eval_groups import assign_groups, class_motion_energy


def test_assign_groups_quantile_boundaries_on_linear_ramp():
    energy = np.arange(9, dtype=float)
    groups = assign_groups(energy, n_groups=3)
    assert groups.tolist() == [0, 0, 0, 1, 1, 1, 2, 2, 2]


def test_assign_groups_ties_go_to_lower_group():
    # quantile([0,0,1,1], 1/3)=0 and quantile(..., 2/3)=1 land exactly on values
    energy = np.array([0.0, 0.0, 1.0, 1.0])
    groups = assign_groups(energy, n_groups=3)
    assert groups.tolist() == [0, 0, 1, 1]


def test_class_motion_energy_shape_and_medians():
    # 2 classes x 3 samples; speed slice 126:168 constant per sample
    x = np.zeros((6, 45, 189), dtype=np.float32)
    y = np.array([0, 0, 0, 1, 1, 1])
    for i, v in enumerate([1.0, 2.0, 3.0, 10.0, -20.0, 30.0]):
        x[i, :, 126:168] = v
    energy = class_motion_energy(x, y)
    assert energy.shape == (2,)
    np.testing.assert_allclose(energy, [2.0, 20.0], rtol=1e-6, atol=1e-6)
