"""T6.1 WS tests: handshake, 45-frame prediction, bad frame, reset, stop.

Auth (Task 9 STRICT-(b)): `?token=` is required and verified against
`JWT_SECRET`; missing or wrong token closes the socket with 4401.
"""

import os
import time

import numpy as np
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app

client = TestClient(app)
FRAMES = (np.random.default_rng(2).normal(0, 0.5, (45, 189))).tolist()

# Same lookup rule as backend/app/routers/stream.py so the suite passes
# whether JWT_SECRET is set in the env or falls back to the default.
SECRET = os.getenv("JWT_SECRET", "change-me")


def test_ws_flow():
    with client.websocket_connect(f"/api/v1/stream?session_id=sess_e2e&token={SECRET}") as ws:
        assert ws.receive_json()["type"] == "status"
        ws.send_json({"type": "start"})
        assert ws.receive_json()["state"] == "Tracking"
        ws.send_json({"type": "heartbeat"})
        assert ws.receive_json()["state"] == "Tracking"
        ws.send_json({"type": "frame", "frame": [0.0] * 10})
        assert ws.receive_json()["type"] == "error"
        for f in FRAMES:
            ws.send_json({"type": "frame", "frame": f})
        pred = ws.receive_json()
        assert pred["type"] == "prediction"
        assert pred["prediction"]["class_id"].startswith("ISL_")
        ws.send_json({"type": "tracking-lost"})
        assert ws.receive_json()["state"] == "Tracking-Lost"
        ws.send_json({"type": "bogus"})
        assert ws.receive_json()["type"] == "error"
        ws.send_json({"type": "stop"})
        assert ws.receive_json()["state"] == "Ready"


def test_ws_rejects_anonymous():
    """No `?token=` → socket closed with 4401, no Ready frame."""
    with client.websocket_connect("/api/v1/stream?session_id=sess_anon") as ws:
        try:
            ws.receive_json()
            raise AssertionError("anonymous handshake should have been closed with 4401")
        except WebSocketDisconnect as e:
            assert e.code == 4401


def test_ws_rejects_wrong_token():
    """Wrong `?token=` → socket closed with 4401, no Ready frame."""
    with client.websocket_connect("/api/v1/stream?session_id=sess_bad&token=wrong-secret") as ws:
        try:
            ws.receive_json()
            raise AssertionError("wrong-token handshake should have been closed with 4401")
        except WebSocketDisconnect as e:
            assert e.code == 4401


def test_ws_malformed_frame_stays_open():
    """['oops']*189 -> error frame, socket usable afterwards."""
    with client.websocket_connect(f"/api/v1/stream?session_id=sess_malformed&token={SECRET}") as ws:
        assert ws.receive_json()["type"] == "status"
        ws.send_json({"type": "start"})
        assert ws.receive_json()["state"] == "Tracking"
        ws.send_json({"type": "frame", "frame": ["oops"] * 189})
        err = ws.receive_json()
        assert err["type"] == "error"
        assert err["code"] == "INVALID_INPUT"
        for f in FRAMES:
            ws.send_json({"type": "frame", "frame": f})
        pred = ws.receive_json()
        assert pred["type"] == "prediction"
        assert pred["prediction"]["class_id"].startswith("ISL_")
        ws.send_json({"type": "stop"})
        assert ws.receive_json()["state"] == "Ready"


def test_ws_nan_frame_rejected():
    """NaN frame -> error frame, no prediction emitted for it."""
    with client.websocket_connect(f"/api/v1/stream?session_id=sess_nan&token={SECRET}") as ws:
        assert ws.receive_json()["type"] == "status"
        ws.send_json({"type": "start"})
        assert ws.receive_json()["state"] == "Tracking"
        for f in FRAMES[:44]:
            ws.send_json({"type": "frame", "frame": f})
        ws.send_json({"type": "frame", "frame": [float("nan")] * 189})
        err = ws.receive_json()
        assert err["type"] == "error"
        assert err["code"] == "INVALID_INPUT"
        # Socket usable: one more good frame completes the window -> prediction.
        ws.send_json({"type": "frame", "frame": FRAMES[44]})
        pred = ws.receive_json()
        assert pred["type"] == "prediction"
        assert pred["prediction"]["class_id"].startswith("ISL_")
        ws.send_json({"type": "stop"})
        assert ws.receive_json()["state"] == "Ready"


def test_ws_blank_frames_yield_no_sign():
    """45 all-zero frames -> prediction with state "No-Sign", never "Recognized"."""
    with client.websocket_connect(f"/api/v1/stream?session_id=sess_blank&token={SECRET}") as ws:
        assert ws.receive_json()["type"] == "status"
        ws.send_json({"type": "start"})
        assert ws.receive_json()["state"] == "Tracking"
        for _ in range(45):
            ws.send_json({"type": "frame", "frame": [0.0] * 189})
        pred = ws.receive_json()
        assert pred["type"] == "prediction"
        assert pred["state"] == "No-Sign", pred
        assert pred["state"] != "Recognized"
        assert "prediction" in pred  # neutral prediction stays attached
        ws.send_json({"type": "stop"})
        assert ws.receive_json()["state"] == "Ready"


def test_ws_recognized_persists_to_history():
    """Stream with a real sid -> GET predictions contains the streamed class."""
    AUTHH = {"Authorization": f"Bearer {SECRET}"}
    sid = client.post("/api/v1/session", json={}, headers=AUTHH).json()["session_id"]
    frames = (np.random.default_rng(1).normal(0, 0.5, (45, 189))).tolist()
    with client.websocket_connect(f"/api/v1/stream?session_id={sid}&token={SECRET}") as ws:
        assert ws.receive_json()["type"] == "status"
        ws.send_json({"type": "start"})
        assert ws.receive_json()["state"] == "Tracking"
        for f in frames:
            ws.send_json({"type": "frame", "frame": f})
        pred = ws.receive_json()
        assert pred["type"] == "prediction"
        assert pred["state"] == "Recognized", pred
        class_id = pred["prediction"]["class_id"]
        # Same class repeated on this socket must not duplicate history rows.
        time.sleep(0.6)  # pass the 500 ms inference throttle
        for f in frames:
            ws.send_json({"type": "frame", "frame": f})
        pred2 = ws.receive_json()
        assert pred2["type"] == "prediction"
        assert pred2["state"] == "Recognized", pred2
        assert pred2["prediction"]["class_id"] == class_id, pred2
        ws.send_json({"type": "stop"})
        assert ws.receive_json()["state"] == "Ready"
    h = client.get(f"/api/v1/sessions/{sid}/predictions", headers=AUTHH).json()
    matches = [p for p in h["predictions"] if p["class_id"] == class_id]
    assert matches, h
    assert len(matches) == 1, f"expected exactly one history row for {class_id}: {h}"
    # No-Sign predictions must NOT be persisted on the same session.
    with client.websocket_connect(f"/api/v1/stream?session_id={sid}&token={SECRET}") as ws:
        assert ws.receive_json()["type"] == "status"
        ws.send_json({"type": "start"})
        assert ws.receive_json()["state"] == "Tracking"
        for _ in range(45):
            ws.send_json({"type": "frame", "frame": [0.0] * 189})
        blank = ws.receive_json()
        assert blank["type"] == "prediction" and blank["state"] == "No-Sign", blank
        ws.send_json({"type": "stop"})
        assert ws.receive_json()["state"] == "Ready"
    h2 = client.get(f"/api/v1/sessions/{sid}/predictions", headers=AUTHH).json()
    assert all(p["class_id"] != "ISL_000" for p in h2["predictions"]), h2
    assert len(h2["predictions"]) == 1, h2


def test_ws_flood_is_bounded():
    """200 rapid frames -> prediction received, round-trip < 30 s."""
    with client.websocket_connect(f"/api/v1/stream?session_id=sess_flood&token={SECRET}") as ws:
        assert ws.receive_json()["type"] == "status"
        ws.send_json({"type": "start"})
        assert ws.receive_json()["state"] == "Tracking"
        t0 = time.monotonic()
        frame = [0.1] * 189
        for _ in range(200):
            ws.send_json({"type": "frame", "frame": frame})
        pred = None
        deadline = t0 + 30  # bounded: a future no-prediction regression fails instead of hanging
        while pred is None:
            if time.monotonic() > deadline:
                raise AssertionError("no prediction within 30 s (flood round-trip deadline exceeded)")
            msg = ws.receive_json()
            if msg.get("type") == "prediction":
                pred = msg
        dt = time.monotonic() - t0
        assert pred["prediction"]["class_id"].startswith("ISL_")
        assert dt < 30, f"flood round-trip took {dt:.1f}s, expected < 30s"
        ws.send_json({"type": "stop"})
        assert ws.receive_json()["state"] == "Ready"
