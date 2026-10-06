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


def test_session_predictions_include_label():  # every item has non-empty "label"
    sid = client.post("/api/v1/session", json={}, headers=AUTH).json()["session_id"]
    r = client.post("/api/v1/predict", json={"frames": FRAMES, "session_id": sid}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    h = client.get(f"/api/v1/sessions/{sid}/predictions", headers=AUTH).json()
    assert h["predictions"], "expected at least one logged prediction"
    for p in h["predictions"]:
        assert p.get("label"), f"prediction missing non-empty label: {p}"


def test_log_failure_is_logged_not_silent(monkeypatch, caplog):
    """Monkeypatched db.add raising -> predict still 200 AND a log record exists."""
    import contextlib
    import logging

    import app.routers.session as sess

    class _FailingDB:
        def get(self, *args, **kwargs):
            return object()  # FK parents present -> reach the failing add
        def add(self, *args, **kwargs):
            raise RuntimeError("db down")
        def commit(self):
            pass

    @contextlib.contextmanager
    def _failing_session():
        yield _FailingDB()

    monkeypatch.setattr(sess, "get_db_session", _failing_session)
    before = sess.PREDICTION_ERRORS_TOTAL._value.get()
    with caplog.at_level(logging.ERROR, logger=sess.logger.name):
        r = client.post("/api/v1/predict", json={"frames": FRAMES, "session_id": "sess_boom"},
                        headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    assert r.json()["prediction"].get("prediction_id", "").startswith("pred_")
    assert sess.PREDICTION_ERRORS_TOTAL._value.get() == before + 1
    assert any(rec.levelno >= logging.ERROR and "log_prediction" in rec.getMessage()
               for rec in caplog.records), "expected log_prediction failure to be logged"
