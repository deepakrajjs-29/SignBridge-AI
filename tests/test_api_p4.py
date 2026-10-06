"""M4 contract matrix (T4.1–T4.5). Set JWT_SECRET=test-secret via env before run."""

import numpy as np
from fastapi.testclient import TestClient

from app.deps import reset_rate_limit
from app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-secret"}
FRAMES = (np.random.default_rng(0).normal(0, 0.5, (45, 189))).tolist()


def setup_function(_):
    reset_rate_limit()


def test_open_endpoints():
    assert client.get("/health").status_code == 200
    assert client.get("/api/v1/model").status_code == 200
    assert client.get("/api/v1/classes").json()["count"] == 50


def test_predict_200_and_alias():
    for path in ("/api/v1/predict", "/api/v1/recognize", "/api/v1/predict/sequence"):
        r = client.post(path, json={"frames": FRAMES}, headers=AUTH)
        assert r.status_code == 200, (path, r.text[:200])
        b = r.json()
        assert b["success"] and b["prediction"]["class_id"].startswith("ISL_")
        assert b["status"] in ("recognized", "uncertain")
        assert "processing_time_ms" in b


def test_predict_auth():
    assert client.post("/api/v1/predict", json={"frames": FRAMES}).status_code == 401
    bad = {"Authorization": "Bearer wrong"}
    assert client.post("/api/v1/predict", json={"frames": FRAMES}, headers=bad).status_code == 403


def test_predict_422_dim_and_413():
    r = client.post("/api/v1/predict", json={"frames": [[0.0] * 120] * 45}, headers=AUTH)
    assert r.status_code == 422 and "189" in r.text
    r = client.post("/api/v1/predict", json={"frames": [[0.0] * 189] * 601}, headers=AUTH)
    assert r.status_code == 413


def test_image_video_501():
    for path in ("/api/v1/predict/image", "/api/v1/predict/video"):
        r = client.post(path, headers=AUTH)
        assert r.status_code == 501 and "CV_UNAVAILABLE" in r.text


def test_session_lifecycle():
    s = client.post("/api/v1/session", json={}, headers=AUTH).json()["session_id"]
    assert s.startswith("sess_")
    assert client.delete(f"/api/v1/session/{s}", headers=AUTH).status_code == 200
    assert client.delete("/api/v1/session/nope", headers=AUTH).status_code == 404


def test_tts_501_and_t2s():
    r = client.post("/api/v1/tts", json={"text": "Hello"}, headers=AUTH)
    assert r.status_code == 501 and "TTS_NOT_CONFIGURED" in r.text
    r = client.post("/api/v1/text-to-sign", json={"text": "Hello xyzzy"}, headers=AUTH).json()
    assert r["items"] and r["unsupported_words"] == ["xyzzy"]


def test_admin_rbac_and_audit():
    assert client.get("/api/v1/admin/models").status_code == 401
    r = client.get("/api/v1/admin/models", headers=AUTH)
    assert r.status_code == 200 and r.json()["models"]
    r = client.post("/api/v1/admin/promote",
                    json={"model_id": "SBAI-MDL-ISL-1.0.0", "environment": "staging"}, headers=AUTH)
    assert r.status_code == 200
    r = client.post("/api/v1/admin/rollback",
                    json={"model_id": "SBAI-MDL-ISL-1.0.0", "environment": "staging"}, headers=AUTH)
    assert r.status_code == 200 and "rolled_back_at" in r.json()


def test_rate_limit_429(monkeypatch):
    import app.deps as deps
    monkeypatch.setattr(deps, "RATE_PER_MIN", 2)
    for _ in range(2):
        client.post("/api/v1/predict", json={"frames": FRAMES}, headers=AUTH)
    assert client.post("/api/v1/predict", json={"frames": FRAMES}, headers=AUTH).status_code == 429
