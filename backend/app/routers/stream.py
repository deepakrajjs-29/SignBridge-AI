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

from app.deps import (FEAT_DIM, SEQ_LEN, decision_status, get_model, get_policy,
                      label_of, model_version, preprocess_window, top_k_alternatives)
from app.metrics import INFER_SECONDS
from app.routers.session import is_session_known, log_prediction

router = APIRouter()


def run_stream_inference(batch: np.ndarray) -> np.ndarray:
    """Pure sync TF inference: (1, SEQ_LEN, FEAT_DIM) batch -> class probs.

    Blocking (~ms-scale `model.predict`); always run via
    `await asyncio.to_thread(...)` so the stream loop stays responsive.
    """
    return get_model().predict(batch, verbose=0)[0]


async def _predict_payload(window_raw: np.ndarray, session_id: str) -> tuple[dict, str, str]:
    """One prediction message for a raw (already-validated) window.

    Shared by the per-frame and `window` message branches so both paths
    produce byte-identical payloads (REST<->WS parity). Includes the
    No-Sign energy-gate short-circuit (pre-normalization — see
    predict.py's Task 11 note): the sentinel ISL_000 payload comes back
    without any model call.

    Returns (payload, state, class_id). Persisting Recognized predictions
    stays in each branch (dedup state last_logged is per-connection).
    """
    t0 = time.perf_counter()
    # Shared pipeline with REST predict.py (Task 5): resample/pad to 45,
    # No-Sign energy gate (pre-normalization), scale — the frame path passes
    # an already-45-row window (identity resample), the window path full-T.
    # Sentinel contract: ISL_000 is intentionally out-of-vocabulary; the
    # carried label ("No sign detected") is what renders; the response is
    # never persisted; argmax is deliberately not attached (model call).
    normed = preprocess_window(window_raw)
    if normed is None:
        return ({
            "type": "prediction", "state": "No-Sign", "session_id": session_id,
            "prediction": {"class_id": "ISL_000", "label": "No sign detected",
                           "confidence": 0.0},
            "alternatives": [],
            "model_version": model_version(),
            "processing_time_ms": round((time.perf_counter() - t0) * 1000, 2),
        }, "No-Sign", "ISL_000")
    tta = int(get_policy().get("tta_windows", 1))
    with INFER_SECONDS.time():
        from app.deps import calibrate_probs, recognize_probs, uses_ensemble

        if uses_ensemble():
            probs = await asyncio.to_thread(recognize_probs, normed, tta)
        else:
            probs = calibrate_probs(
                await asyncio.to_thread(run_stream_inference, normed[None])
            )
    ci, conf = int(probs.argmax()), float(probs.max())
    state = decision_status(conf, get_policy()).capitalize()
    class_id = f"ISL_{ci + 1:03d}"
    return ({
        "type": "prediction", "state": state, "session_id": session_id,
        "prediction": {"class_id": class_id, "label": label_of(class_id),
                       "confidence": round(conf, 4)},
        "alternatives": top_k_alternatives(probs, k=4),
        "model_version": model_version(),
        "processing_time_ms": round((time.perf_counter() - t0) * 1000, 2),
    }, state, class_id)


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
                    # first window (last_infer None) always infers immediately
                    window = np.asarray(buf[-SEQ_LEN:], dtype="float32")
                    payload, state, class_id = await _predict_payload(window, session_id)
                    # Clock starts when the inference FINISHES: if it took >= 500 ms,
                    # setting the stamp before (old behavior) let a queued burst frame
                    # pass the throttle instantly and fire a second prediction right
                    # after the first (flaky test_ws_flood_is_bounded, real double-load).
                    last_infer = time.monotonic()
                    await ws.send_json(payload)
                    # Task 13: persist Recognized predictions to History via
                    # log_prediction, only when the class differs from the last
                    # logged one on this socket. No-Sign/Provisional/Uncertain
                    # never persist.
                    if state == "Recognized" and class_id != last_logged:
                        log_prediction(session_id, class_id,
                                       payload["prediction"]["confidence"], model_version())
                        last_logged = class_id
            elif kind == "window":
                # Full-T client-side window (Task 5): the browser captured a
                # whole attempt, resampled/padded it to 45 rows on the client
                # (hands.buildFeatureRows) and ships it as one message — no
                # rolling buffer involved. Envelope mirrors REST predict.py:
                # 1..600 rows, each exactly FEAT_DIM finite floats (bools
                # rejected), else the existing INVALID_INPUT error shape.
                frames = msg.get("frames")
                if (not isinstance(frames, list) or not 1 <= len(frames) <= 600
                        or any(not isinstance(row, list) or len(row) != FEAT_DIM
                               or any(isinstance(v, bool) or not isinstance(v, (int, float))
                                      or not math.isfinite(float(v)) for v in row)
                               for row in frames)):
                    await ws.send_json({
                        "type": "error", "code": "INVALID_INPUT",
                        "message": f"window must be 1-600 rows of {FEAT_DIM} finite floats"})
                    continue
                buf = frames  # a window replaces the rolling buffer
                window = np.asarray(frames, dtype="float32")
                payload, state, class_id = await _predict_payload(window, session_id)
                last_infer = time.monotonic()  # bypass throttle for THIS message (it always infers); keep subsequent frame path on the same completion-based clock
                await ws.send_json(payload)
                # Identical persistence rule as the frame path.
                if state == "Recognized" and class_id != last_logged:
                    log_prediction(session_id, class_id,
                                   payload["prediction"]["confidence"], model_version())
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
