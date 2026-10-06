"""T6.1 WS tests: handshake, 45-frame prediction, bad frame, reset, stop.

Auth (Task 9 STRICT-(b)): `?token=` is required and verified against
`JWT_SECRET`; missing or wrong token closes the socket with 4401.
"""

import os

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
