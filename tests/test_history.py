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


def test_close_marks_closed_and_purge_removes():  # Task 12: real close (DB closed) + children-first purge
    from app.deps import get_db_session
    from app.models import Prediction, RecognitionSession
    sid = client.post("/api/v1/session", json={}, headers=AUTH).json()["session_id"]
    r = client.post("/api/v1/predict", json={"frames": FRAMES, "session_id": sid}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    pid = r.json()["prediction"]["prediction_id"]
    assert pid
    assert client.delete(f"/api/v1/session/{sid}", headers=AUTH).status_code == 200
    with get_db_session() as db:
        row = db.get(RecognitionSession, sid)
        assert row is not None and row.status == "closed", row
    # closed session rejects new predictions as unknown
    r = client.post("/api/v1/predict", json={"frames": FRAMES, "session_id": sid}, headers=AUTH)
    assert r.status_code == 404 and "UNKNOWN_SESSION" in r.text, r.text[:200]
    # purge removes children-first (feedback -> predictions -> session row)
    assert client.delete(f"/api/v1/sessions/{sid}/purge", headers=AUTH).status_code == 200
    with get_db_session() as db:
        assert db.get(RecognitionSession, sid) is None
        assert db.query(Prediction).filter(Prediction.session_id == sid).all() == []
    # purging twice: second purge is 404 unknown
    assert client.delete(f"/api/v1/sessions/{sid}/purge", headers=AUTH).status_code == 404


def test_sessions_limit_clamped():  # Task 17: limit=1000 -> at most 200 items on both list endpoints
    from app.routers.session import log_prediction
    # seed >200 sessions (session open carries no rate limit)
    for _ in range(210):
        r = client.post("/api/v1/session", json={}, headers=AUTH)
        assert r.status_code == 200, r.text[:200]
    r = client.get("/api/v1/sessions?limit=1000", headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    assert len(r.json()["sessions"]) <= 200
    # default limit is 50
    r = client.get("/api/v1/sessions", headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    assert len(r.json()["sessions"]) <= 50
    # predictions list clamped too: seed via log_prediction (bypasses predict rate limit)
    sid = client.post("/api/v1/session", json={}, headers=AUTH).json()["session_id"]
    for _ in range(210):
        log_prediction(sid, "ISL_001", 0.9, "signbridge-gru-v1")
    r = client.get(f"/api/v1/sessions/{sid}/predictions?limit=1000", headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    assert len(r.json()["predictions"]) <= 200
    r = client.get(f"/api/v1/sessions/{sid}/predictions", headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    assert len(r.json()["predictions"]) <= 50
