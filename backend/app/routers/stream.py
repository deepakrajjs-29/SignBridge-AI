"""T6.1 — WebSocket /api/v1/stream (rolling 45-frame buffer, reset on stop/loss).

Auth (Task 9 fix round 1, STRICT-(b) per controller): `?token=` is REQUIRED on
every handshake and verified against `JWT_SECRET` (same shared secret as the
REST Bearer rule); a missing OR mismatched token closes the socket with 4401
before any Ready/status frame is sent. Anonymous sockets are never admitted.
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.deps import FEAT_DIM, SEQ_LEN, get_model, get_policy, get_scaler, label_of, model_version
from app.metrics import INFER_SECONDS

router = APIRouter()


def run_stream_inference(batch: np.ndarray) -> np.ndarray:
    """Pure sync TF inference: (1, SEQ_LEN, FEAT_DIM) batch -> class probs.

    Blocking (~ms-scale `model.predict`); always run via
    `await asyncio.to_thread(...)` so the stream loop stays responsive.
    """
    return get_model().predict(batch, verbose=0)[0]


@router.websocket("/stream")
async def stream(ws: WebSocket):
    await ws.accept()
    token = ws.query_params.get("token")
    if token != os.getenv("JWT_SECRET", "change-me"):
        await ws.close(code=4401)
        return
    session_id = ws.query_params.get("session_id", f"sess_{uuid.uuid4().hex[:8]}")
    buf: list[list[float]] = []
    await ws.send_json({"type": "status", "state": "Ready", "session_id": session_id})
    try:
        while True:
            msg = await ws.receive_json()
            kind = msg.get("type")
            if kind == "start":
                buf.clear()
                await ws.send_json({"type": "status", "state": "Tracking", "session_id": session_id})
            elif kind == "frame":
                frame = msg.get("frame")
                if not isinstance(frame, list) or len(frame) != FEAT_DIM:
                    await ws.send_json({"type": "error", "code": "INVALID_INPUT",
                                        "message": f"frame must be {FEAT_DIM} floats"})
                    continue
                buf.append(frame)
                if len(buf) >= SEQ_LEN:
                    window = np.asarray(buf[-SEQ_LEN:], dtype="float32")
                    mu, sd = get_scaler()
                    t0 = time.perf_counter()
                    with INFER_SECONDS.time():
                        probs = await asyncio.to_thread(
                            run_stream_inference,
                            ((window - mu.reshape(189)) / sd.reshape(189)).astype("float32")[None],
                        )
                    ci, conf = int(probs.argmax()), float(probs.max())
                    policy = get_policy()
                    state = "Recognized" if conf >= float(policy.get("threshold", 0.4)) else "Uncertain"
                    await ws.send_json({
                        "type": "prediction", "state": state, "session_id": session_id,
                        "prediction": {"class_id": f"ISL_{ci + 1:03d}",
                                       "label": label_of(f"ISL_{ci + 1:03d}"),
                                       "confidence": round(conf, 4)},
                        "model_version": model_version(),
                        "processing_time_ms": round((time.perf_counter() - t0) * 1000, 2)})
            elif kind == "heartbeat":
                await ws.send_json({"type": "status", "state": "Tracking", "session_id": session_id})
            elif kind in ("stop", "tracking-lost"):
                buf.clear()
                await ws.send_json({"type": "status",
                                    "state": "Ready" if kind == "stop" else "Tracking-Lost",
                                    "session_id": session_id})
                if kind == "stop":
                    break
            else:
                await ws.send_json({"type": "error", "code": "UNKNOWN_TYPE",
                                    "message": f"unknown message type: {kind}"})
    except WebSocketDisconnect:
        return
