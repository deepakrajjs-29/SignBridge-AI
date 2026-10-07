"""T6.1 — WebSocket /api/v1/stream (rolling 45-frame buffer, reset on stop/loss).

Auth (Task 9 fix round 1, STRICT-(b) per controller): `?token=` is REQUIRED on
every handshake and verified against `JWT_SECRET` (same shared secret as the
REST Bearer rule); a missing OR mismatched token closes the socket with 4401
before any Ready/status frame is sent. Anonymous sockets are never admitted.

Session (Task 13 fix round 1): `?session_id=` must already exist — created via
`POST /api/v1/session`, i.e. known to `is_session_known()` (live in-memory
table and/or an active DB row, mirroring the REST UNKNOWN_SESSION rule). A
missing or unknown id gets `{"type":"error","code":"UNKNOWN_SESSION",...}`
followed by close(4404); NOTHING is created and nothing is persisted.
"""

from __future__ import annotations

import asyncio
import math
import os
import time

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.deps import FEAT_DIM, NOSIGN_ENERGY, SEQ_LEN, get_model, get_policy, get_scaler, label_of, model_version
from app.metrics import INFER_SECONDS
from app.routers.session import is_session_known, log_prediction

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
    session_id = ws.query_params.get("session_id", "")
    # Task 13 fix round 1: parity with the REST UNKNOWN_SESSION rule (Task 12)
    # — never auto-register. Unknown/missing ids are rejected here so the WS
    # path cannot reopen the ghost-session hole; log_prediction()'s lazy row
    # is then only ever reached for already-known sessions.
    if not session_id or not is_session_known(session_id):
        await ws.send_json({"type": "error", "code": "UNKNOWN_SESSION",
                            "message": "unknown session"})
        await ws.close(code=4404)
        return
    buf: list[list[float]] = []
    last_infer: float | None = None  # monotonic timestamp of last inference (500 ms throttle)
    last_logged: str | None = None  # class_id of the last persisted prediction on this socket
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
                # REST parity (predict.py): list, len == FEAT_DIM, all-finite floats.
                # Reject before append so a bad frame never poisons the window or
                # reaches np.asarray (which would raise and wedge the socket).
                if (not isinstance(frame, list) or len(frame) != FEAT_DIM
                        or any(isinstance(v, bool) or not isinstance(v, (int, float))
                               or not math.isfinite(float(v)) for v in frame)):
                    await ws.send_json({"type": "error", "code": "INVALID_INPUT",
                                        "message": f"frame must be {FEAT_DIM} floats"})
                    continue
                buf.append(frame)
                buf = buf[-SEQ_LEN:]  # rolling cap: buffer never exceeds one window
                if len(buf) >= SEQ_LEN:
                    now = time.monotonic()
                    if last_infer is not None and (now - last_infer) < 0.5:
                        continue  # backpressure: at most one inference per 500 ms
                    last_infer = now  # first window (None) always infers immediately
                    window = np.asarray(buf[-SEQ_LEN:], dtype="float32")
                    t0 = time.perf_counter()
                    # No-Sign energy gate (Task 11): blank windows answer
                    # "No-Sign" BEFORE any model call (same rule as predict.py;
                    # checked pre-normalization — see predict.py note).
                    # Sentinel contract: ISL_000 is intentionally
                    # out-of-vocabulary; the carried label ("No sign detected")
                    # is what renders; the response is never persisted;
                    # argmax is deliberately not attached (model call).
                    if float(np.abs(window).max()) < NOSIGN_ENERGY:
                        await ws.send_json({
                            "type": "prediction", "state": "No-Sign", "session_id": session_id,
                            "prediction": {"class_id": "ISL_000",
                                           "label": "No sign detected",
                                           "confidence": 0.0},
                            "model_version": model_version(),
                            "processing_time_ms": round((time.perf_counter() - t0) * 1000, 2)})
                        continue
                    mu, sd = get_scaler()
                    with INFER_SECONDS.time():
                        probs = await asyncio.to_thread(
                            run_stream_inference,
                            ((window - mu.reshape(189)) / sd.reshape(189)).astype("float32")[None],
                        )
                    ci, conf = int(probs.argmax()), float(probs.max())
                    policy = get_policy()
                    state = "Recognized" if conf >= float(policy.get("threshold", 0.4)) else "Uncertain"
                    class_id = f"ISL_{ci + 1:03d}"
                    await ws.send_json({
                        "type": "prediction", "state": state, "session_id": session_id,
                        "prediction": {"class_id": class_id,
                                       "label": label_of(class_id),
                                       "confidence": round(conf, 4)},
                        "model_version": model_version(),
                        "processing_time_ms": round((time.perf_counter() - t0) * 1000, 2)})
                    # Task 13: persist Recognized predictions to History via
                    # log_prediction, only when the class differs from the last
                    # logged one on this socket. No-Sign/Uncertain never persist.
                    if state == "Recognized" and class_id != last_logged:
                        log_prediction(session_id, class_id, round(conf, 4), model_version())
                        last_logged = class_id
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
