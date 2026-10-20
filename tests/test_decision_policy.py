"""Task 3 — three-state decision policy (Accepted / Provisional / Uncertain).

Pins deps.decision_status: inclusive boundaries, two-state fallback when
provisional_threshold is absent, and the live fitted policy shape written by
scripts/calibrate_v4.py.
"""
from app import deps


def test_boundaries_inclusive():
    pol = {"accept_threshold": 0.6, "provisional_threshold": 0.3}
    assert deps.decision_status(0.6, pol) == "recognized"
    assert deps.decision_status(0.3, pol) == "provisional"
    assert deps.decision_status(0.2999, pol) == "uncertain"


def test_missing_keys_stay_two_state():
    assert deps.decision_status(0.5, {"threshold": 0.4}) == "recognized"
    assert deps.decision_status(0.39, {"threshold": 0.4}) == "uncertain"
    # provisional collapses onto accept when absent -> no provisional band
    pol = {"accept_threshold": 0.6}
    assert deps.decision_status(0.5, pol) == "uncertain"


def test_live_policy_shape():
    pol = deps.get_policy()
    assert pol["threshold"] == pol["accept_threshold"]
    assert 0 <= pol["provisional_threshold"] <= pol["accept_threshold"] <= 1
