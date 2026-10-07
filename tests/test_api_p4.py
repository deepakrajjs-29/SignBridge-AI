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
    from app.deps import MODELS
    reg_path = MODELS / "registry.json"
    saved = reg_path.read_bytes()  # promote rewrites the live registry: restore after
    try:
        r = client.post("/api/v1/admin/promote",
                        json={"model_id": "SBAI-MDL-ISL-1.0.0", "environment": "staging"}, headers=AUTH)
        assert r.status_code == 200
    finally:
        reg_path.write_bytes(saved)
    r = client.post("/api/v1/admin/rollback",
                    json={"model_id": "SBAI-MDL-ISL-1.0.0", "environment": "staging"}, headers=AUTH)
    assert r.status_code == 200 and "rolled_back_at" in r.json()


def test_rate_limit_429(monkeypatch):
    import app.deps as deps
    monkeypatch.setattr(deps, "RATE_PER_MIN", 2)
    for _ in range(2):
        client.post("/api/v1/predict", json={"frames": FRAMES}, headers=AUTH)
    r = client.post("/api/v1/predict", json={"frames": FRAMES}, headers=AUTH)
    assert r.status_code == 429
    b = r.json()
    assert b["success"] is False
    assert b["error"]["code"] == "RATE_LIMITED"
    assert b.get("request_id")


def test_single_classes_route():  # exactly one route object serves GET /api/v1/classes
    matches = []
    for r in app.routes:
        if getattr(r, "path", "") == "/api/v1/classes" and "GET" in (getattr(r, "methods", None) or set()):
            matches.append(r)
        inner = getattr(getattr(r, "original_router", None), "routes", None) or []
        prefix = getattr(getattr(r, "include_context", None), "prefix", "") or ""
        for q in inner:
            if prefix + getattr(q, "path", "") == "/api/v1/classes" \
                    and "GET" in (getattr(q, "methods", None) or set()):
                matches.append(q)
    assert len(matches) == 1, f"expected exactly one GET /api/v1/classes route, found {len(matches)}"


def test_unauthorized_uses_envelope():  # POST /api/v1/predict, no token -> envelope shape
    r = client.post("/api/v1/predict", json={"frames": FRAMES})
    assert r.status_code == 401
    b = r.json()
    assert b["success"] is False
    assert b["error"]["code"] == "UNAUTHORIZED"
    assert b.get("request_id")


def test_403_uses_envelope():  # wrong Bearer token -> 403 envelope shape
    r = client.post("/api/v1/predict", json={"frames": FRAMES},
                    headers={"Authorization": "Bearer wrong"})
    assert r.status_code == 403
    b = r.json()
    assert b["success"] is False
    assert b["error"]["code"] == "FORBIDDEN"
    assert b.get("request_id")


def test_text_to_sign_multiword():  # "thank you" -> items [ISL_002], unsupported []
    r = client.post("/api/v1/text-to-sign", json={"text": "thank you"}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    b = r.json()
    assert [i["class_id"] for i in b["items"]] == ["ISL_002"]
    assert b["unsupported_words"] == []
    r = client.post("/api/v1/text-to-sign", json={"text": "good morning"}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    b = r.json()
    assert [i["class_id"] for i in b["items"]] == ["ISL_008"]
    assert b["unsupported_words"] == []
    r = client.post("/api/v1/text-to-sign", json={"text": "hello xyz"}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    b = r.json()
    assert [i["class_id"] for i in b["items"]] == ["ISL_001"]
    assert b["unsupported_words"] == ["xyz"]


def test_promote_switches_active_model():  # promote X -> GET /model reports X (restore registry after)
    import json
    from app.deps import MODELS
    reg_path = MODELS / "registry.json"
    original = reg_path.read_bytes()  # TRACKED live file: byte-exact restore in finally
    try:
        r = client.post("/api/v1/admin/promote",
                        json={"model_id": "SBAI-MDL-ISL-9.9.9-test", "environment": "staging"},
                        headers=AUTH)
        assert r.status_code == 200, r.text[:200]
        b = client.get("/api/v1/model").json()
        assert b["model"]["model_version"] == "SBAI-MDL-ISL-9.9.9-test", b
        persisted = json.loads(reg_path.read_text(encoding="utf-8"))
        assert persisted.get("active_model") == "SBAI-MDL-ISL-9.9.9-test", persisted
    finally:
        reg_path.write_bytes(original)


def test_parallel_predicts_overlap():  # 4 concurrent predicts wall-time < 3x single-predict wall-time
    import asyncio
    import time as _time

    import httpx

    async def _one(cli):
        r = await cli.post("/api/v1/predict", json={"frames": FRAMES}, headers=AUTH)
        assert r.status_code == 200, r.text[:200]
        return r.json()

    async def _run(n):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as cli:
            await _one(cli)  # untimed warmup: cold TF load + graph trace, outside the measurement
            t0 = _time.perf_counter()
            await _one(cli)
            single = _time.perf_counter() - t0
            t0 = _time.perf_counter()
            await asyncio.gather(*[_one(cli) for _ in range(n)])
            total = _time.perf_counter() - t0
            return single, total

    single, total = asyncio.run(_run(4))
    print(f"\n[overlap] single={single:.3f}s total4={total:.3f}s ratio={total / single:.2f}x")
    assert total < 3 * single, f"no overlap: single={single:.3f}s total4={total:.3f}s"


def test_blank_frames_yield_no_sign():  # zeros -> status "no-sign", not recognized
    zeros = [[0.0] * 189] * 45
    r = client.post("/api/v1/predict", json={"frames": zeros}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    b = r.json()
    assert b["success"] is True
    assert b["status"] == "no-sign", b
    assert b["status"] != "recognized"
    assert "prediction" in b  # neutral prediction stays attached, never recognized


def test_prod_refuses_default_secret():  # APP_ENV=production + JWT_SECRET=change-me -> create_app raises RuntimeError
    import pytest
    from app.main import create_app
    import os
    old_env, old_secret = os.getenv("APP_ENV"), os.getenv("JWT_SECRET")
    os.environ["APP_ENV"] = "production"
    os.environ["JWT_SECRET"] = "change-me"
    try:
        with pytest.raises(RuntimeError):
            create_app()
    finally:
        if old_env is None:
            os.environ.pop("APP_ENV", None)
        else:
            os.environ["APP_ENV"] = old_env
        if old_secret is None:
            os.environ.pop("JWT_SECRET", None)
        else:
            os.environ["JWT_SECRET"] = old_secret
