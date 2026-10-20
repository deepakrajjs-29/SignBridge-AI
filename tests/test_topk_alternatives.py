"""Top-k alternatives: real calibrated probs only — no invented labels/scores."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.deps import label_of, top_k_alternatives  # noqa: E402


def test_top_k_sorted_descending_and_real_labels():
    probs = np.zeros(109, dtype="float32")
    probs[3] = 0.40  # ISL_004
    probs[10] = 0.25  # ISL_011
    probs[7] = 0.20  # ISL_008
    probs[0] = 0.15  # ISL_001
    out = top_k_alternatives(probs, k=4)
    assert len(out) == 4
    assert out[0]["class_id"] == "ISL_004"
    assert out[1]["class_id"] == "ISL_011"
    assert out[0]["confidence"] >= out[1]["confidence"] >= out[2]["confidence"]
    for item in out:
        assert item["label"] == label_of(item["class_id"])
        assert 0.0 <= item["confidence"] <= 1.0


def test_top_k_respects_k_and_empty():
    probs = np.full(109, 0.01, dtype="float32")
    assert len(top_k_alternatives(probs, k=3)) == 3
    assert top_k_alternatives(np.array([], dtype="float32"), k=4) == []


def test_rest_predict_returns_alternatives(monkeypatch):
    import pytest
    from fastapi.testclient import TestClient

    from app.main import app
    from app.deps import get_policy

    client = TestClient(app)
    hdr = {"Authorization": "Bearer test-secret"}
    # blank 45x189 -> no-sign path must still return empty alternatives list
    body = {"session_id": "", "frames": [[0.0] * 189] * 45}
    r = client.post("/api/v1/predict", json=body, headers=hdr)
    assert r.status_code == 200
    assert "alternatives" in r.json()
    assert r.json()["alternatives"] == []

    # Non-blank finite window exercises the model path (may be no-sign if
    # energy gate fires after scaling — either way alternatives key exists).
    rng = np.random.default_rng(7)
    noisy = rng.normal(0.0, 1.0, size=(45, 189)).astype(float).tolist()
    r2 = client.post("/api/v1/predict", json={"frames": noisy, "session_id": ""}, headers=hdr)
    assert r2.status_code == 200
    js = r2.json()
    assert "alternatives" in js
    if js["status"] != "no-sign":
        alts = js["alternatives"]
        assert 1 <= len(alts) <= 4
        assert alts[0]["class_id"] == js["prediction"]["class_id"]
        assert alts[0]["confidence"] == js["prediction"]["confidence"]
