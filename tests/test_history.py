"""History read/delete endpoints (T5.0 backend gap)."""

import numpy as np
from fastapi.testclient import TestClient

from app.deps import reset_rate_limit
from app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-secret"}
FRAMES = (np.random.default_rng(1).normal(0, 0.5, (45, 189))).tolist()


def setup_function(_):
    reset_rate_limit()


def test_predict_with_session_logs_and_history_reads():
    sid = client.post("/api/v1/session", json={}, headers=AUTH).json()["session_id"]
    r = client.post("/api/v1/predict", json={"frames": FRAMES, "session_id": sid}, headers=AUTH)
    assert r.status_code == 200
    pid = r.json()["prediction"].get("prediction_id")
    assert pid
    h = client.get(f"/api/v1/sessions/{sid}/predictions", headers=AUTH).json()
    assert any(p["prediction_id"] == pid for p in h["predictions"])
    assert client.get("/api/v1/sessions", headers=AUTH).json()["sessions"]
    assert client.delete(f"/api/v1/history/{pid}", headers=AUTH).status_code == 200
    h2 = client.get(f"/api/v1/sessions/{sid}/predictions", headers=AUTH).json()
    assert all(p["prediction_id"] != pid for p in h2["predictions"])
    assert client.get("/api/v1/sessions/nope/predictions", headers=AUTH).status_code == 404
