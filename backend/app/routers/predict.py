"""T4.1 — prediction endpoints with real inference (45,189).

Task 7: weights resolve via app.deps.get_model() from the registry-active
model (SBAI-MDL-ISL-2.0.0 Softmax100); class ids render ISL_001-100 through
label_of(), envelopes 422/413/429 unchanged."""

from __future__ import annotations

import asyncio
import time
import uuid

import numpy as np
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.deps import (FEAT_DIM, decision_status, get_model, get_policy, label_of,
                      model_version, preprocess_window, rate_limit, require_auth,
                      top_k_alternatives)
from app.metrics import INFER_SECONDS

router = APIRouter()


class PredictBody(BaseModel):
    frames: list[list[float]] = Field(..., description="T x 189 landmark features")
    sequence_id: str = ""
    session_id: str = ""


def run_inference(batch: np.ndarray) -> np.ndarray:
    """Pure sync TF inference: (1, SEQ_LEN, FEAT_DIM) batch -> class probs.

    Blocking (~ms-scale `model.predict`); always run via
    `await asyncio.to_thread(...)` so the event loop stays free.
    """
    return get_model().predict(batch, verbose=0)[0]


async def infer(body: PredictBody, request: Request) -> JSONResponse:
    t0 = time.perf_counter()
    arr = np.asarray(body.frames, dtype="float32")
    if arr.ndim != 2 or arr.shape[1] != FEAT_DIM:
        got = arr.shape[1] if arr.ndim == 2 else -1
        return JSONResponse(status_code=422, content={
            "success": False,
            "error": {"code": "INVALID_INPUT",
                      "message": f"expected feature dim {FEAT_DIM}, got {got}",
                      "details": {"expected": FEAT_DIM, "received": got}},
            "request_id": getattr(request.state, "request_id", "")})
    if not np.all(np.isfinite(arr)):
        return JSONResponse(status_code=422, content={
            "success": False,
            "error": {"code": "INVALID_INPUT", "message": "NaN/Inf rejected", "details": {}},
            "request_id": getattr(request.state, "request_id", "")})
    if len(arr) > 600:
        return JSONResponse(status_code=413, content={
            "success": False,
            "error": {"code": "PAYLOAD_TOO_LARGE", "message": "max 600 frames", "details": {}},
            "request_id": getattr(request.state, "request_id", "")})
    # Task 12: reject ghost sessions — unknown non-empty session_id 404s;
    # empty stays session-less exactly as today (no 404 for empty).
    if body.session_id:
        from app.routers.session import is_session_known
        if not is_session_known(body.session_id):
            return JSONResponse(status_code=404, content={
                "success": False,
                "error": {"code": "UNKNOWN_SESSION", "message": "unknown session", "details": {}},
                "request_id": getattr(request.state, "request_id", "")})
    # fixed 45-frame window: uniform-sample / repeat-pad (same as training),
    # then the Task 11 No-Sign energy gate (PRE-normalization — see the note
    # in deps.preprocess_window), then scaling — all three shared with the
    # WS `window` branch so REST and WS answer identically.
    # Sentinel contract: ISL_000 is intentionally out-of-vocabulary; the
    # carried label ("No sign detected") is what renders; the response is
    # never persisted (prediction_id ""); argmax is deliberately not
    # attached (it would require a model call).
    normed = preprocess_window(arr)
    if normed is None:
        ms = round((time.perf_counter() - t0) * 1000, 2)
        return JSONResponse(content={
            "success": True,
            "prediction": {"class_id": "ISL_000", "label": "No sign detected",
                           "confidence": 0.0, "prediction_id": ""},
            "alternatives": [],
            "status": "no-sign", "model_version": model_version(),
            "processing_time_ms": ms, "sequence_id": body.sequence_id or f"seq_{uuid.uuid4().hex[:8]}",
            "request_id": getattr(request.state, "request_id", "")})
    tta = int(get_policy().get("tta_windows", 1))
    with INFER_SECONDS.time():
        from app.deps import calibrate_probs, recognize_probs, uses_ensemble

        if uses_ensemble():
            probs = await asyncio.to_thread(recognize_probs, normed, tta)
        else:
            probs = calibrate_probs(await asyncio.to_thread(run_inference, normed[None]))
    ci = int(probs.argmax())
    conf = float(probs[ci])
    policy = get_policy()
    status = decision_status(conf, policy)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    pid = ""
    if body.session_id:
        from app.routers.session import log_prediction
        pid = log_prediction(body.session_id, f"ISL_{ci + 1:03d}", round(conf, 4), model_version())
    return JSONResponse(content={
        "success": True,
        "prediction": {"class_id": f"ISL_{ci + 1:03d}", "label": label_of(f"ISL_{ci + 1:03d}"),
                       "confidence": round(conf, 4), "prediction_id": pid},
        "alternatives": top_k_alternatives(probs, k=4),
        "status": status, "model_version": model_version(),
        "processing_time_ms": ms, "sequence_id": body.sequence_id or f"seq_{uuid.uuid4().hex[:8]}",
        "request_id": getattr(request.state, "request_id", "")})


@router.post("/predict")
async def predict(body: PredictBody, request: Request, _=Depends(require_auth), __=Depends(rate_limit)):
    return await infer(body, request)


@router.post("/recognize")
async def recognize_alias(body: PredictBody, request: Request, _=Depends(require_auth), __=Depends(rate_limit)):
    return await infer(body, request)


@router.post("/predict/sequence")
async def predict_sequence(body: PredictBody, request: Request, _=Depends(require_auth), __=Depends(rate_limit)):
    return await infer(body, request)


@router.post("/predict/image")
async def predict_image(request: Request, _=Depends(require_auth)):
    return JSONResponse(status_code=501, content={
        "success": False,
        "error": {"code": "CV_UNAVAILABLE",
                  "message": "MediaPipe image pipeline requires the py3.11 container (P8); use /predict with landmarks until then.",
                  "details": {}},
        "request_id": getattr(request.state, "request_id", "")})


@router.post("/predict/video")
async def predict_video(request: Request, _=Depends(require_auth)):
    return JSONResponse(status_code=501, content={
        "success": False,
        "error": {"code": "CV_UNAVAILABLE",
                  "message": "MediaPipe video pipeline requires the py3.11 container (P8); use /predict/sequence with landmarks until then.",
                  "details": {}},
        "request_id": getattr(request.state, "request_id", "")})
