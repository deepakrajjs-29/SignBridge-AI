"""T6.1 WS tests: handshake, 45-frame prediction, bad frame, reset, stop."""

import numpy as np
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
FRAMES = (np.random.default_rng(2).normal(0, 0.5, (45, 189))).tolist()


def test_ws_flow():
    with client.websocket_connect("/api/v1/stream?session_id=sess_e2e") as ws:
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
