"""Task 7: backend serves 100 classes + text-to-sign photo URIs, model 2.0.0.

RED: /model reports 1.0.0 (registry not promoted), text-to-sign has no
photo rows on an unseeded DB.
GREEN: registry active_model=2.0.0, live DB seeded with 100 photo assets.
"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "database" / "migrations"))

os.environ.setdefault("JWT_SECRET", "test-secret")

from app.deps import reset_rate_limit  # noqa: E402
from app.main import app  # noqa: E402

import m3_seed_100  # noqa: E402

AUTH = {"Authorization": "Bearer test-secret"}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Isolated file-backed DB (NOT :memory:: separate engines must share rows)."""
    db_file = tmp_path / "t7.db"
    url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", url)
    from sqlalchemy import create_engine

    engine = create_engine(url)
    n_classes, n_photos = m3_seed_100.seed_100(engine)
    assert (n_classes, n_photos) == (100, 100)
    engine.dispose()
    reset_rate_limit()
    yield TestClient(app)
    reset_rate_limit()


def test_classes_100_and_text_to_sign_photo(client):
    assert len(client.get("/api/v1/classes").json()["classes"]) == 100
    r = client.post("/api/v1/text-to-sign", json={"text": "good where city"}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    body = r.json()
    assert body["success"] is True
    assert [i["word"] for i in body["items"]] == ["good", "where", "city"]
    assert body["unsupported_words"] == []
    assert all(i["asset_uri"] for i in body["items"])
    assert all(i["supported"] for i in body["items"])


def test_model_is_2_0_0(client):
    b = client.get("/api/v1/model").json()
    assert b["success"] is True
    assert b["model"]["model_version"] == "SBAI-MDL-ISL-3.0.0"
    assert b["model"]["classes"] == 100
    assert "Softmax100" in b["model"]["architecture"]


def test_text_to_sign_longest_phrase_first_and_escape(client):
    # "thank you" matches the 2-word phrase ISL_002, not 1-word leftovers.
    b = client.post("/api/v1/text-to-sign", json={"text": "thank you"}, headers=AUTH).json()
    assert [i["class_id"] for i in b["items"]] == ["ISL_002"]
    assert b["unsupported_words"] == []
    # LIKE wildcards must not match arbitrary classes: reported unsupported.
    b = client.post("/api/v1/text-to-sign", json={"text": "%"}, headers=AUTH).json()
    assert b["items"] == [] and b["unsupported_words"] == ["%"]
    # Photo-URI join shape on a single word.
    b = client.post("/api/v1/text-to-sign", json={"text": "hello"}, headers=AUTH).json()
    assert b["items"][0]["asset_uri"].startswith("/assets/")
    assert b["items"][0]["supported"] is True


def test_predict_envelopes_preserved(client):
    r = client.post("/api/v1/predict", json={"frames": [[0.0] * 120] * 45}, headers=AUTH)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_INPUT"
    r = client.post("/api/v1/predict", json={"frames": [[0.0] * 189] * 601}, headers=AUTH)
    assert r.status_code == 413


def test_rate_limit_429_envelope(client, monkeypatch):
    import app.deps as deps_mod
    monkeypatch.setattr(deps_mod, "RATE_PER_MIN", 2)
    zeros = [[0.0] * 189] * 45  # no-sign path: fast, no TF call
    for _ in range(2):
        assert client.post("/api/v1/predict", json={"frames": zeros}, headers=AUTH).status_code == 200
    r = client.post("/api/v1/predict", json={"frames": zeros}, headers=AUTH)
    assert r.status_code == 429
    b = r.json()
    assert b["success"] is False
    assert b["error"]["code"] == "RATE_LIMITED"
    assert b.get("request_id")
