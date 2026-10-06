from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["status"] == "ok"
    assert "X-Request-ID" in r.headers


def test_model_stub():
    r = client.get("/api/v1/model")
    assert r.status_code == 200
    body = r.json()
    assert body["model"]["seq_len"] == 45
    assert body["model"]["feat_dim"] == 189


def test_classes_count():
    r = client.get("/api/v1/classes")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 50
    assert body["classes"][0]["class_id"] == "ISL_001"
