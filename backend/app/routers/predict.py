"""T4.1 — prediction endpoints with real GRU inference (45,189)."""

from __future__ import annotations

import asyncio
import time
import uuid

import numpy as np
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.deps import (FEAT_DIM, SEQ_LEN, get_model, get_policy, get_scaler,
                      label_of, model_version, rate_limit, require_auth)
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
    # fixed 45-frame window: uniform-sample / repeat-pad (same as training)
    if len(arr) >= SEQ_LEN:
        idx = np.linspace(0, len(arr) - 1, SEQ_LEN).astype(int)
        seq = arr[idx]
    else:
        seq = np.concatenate([arr, np.tile(arr[-1:], (SEQ_LEN - len(arr), 1))])
    mu, sd = get_scaler()
    normed = ((seq - mu.reshape(189)) / sd.reshape(189)).astype("float32")
    with INFER_SECONDS.time():
        probs = await asyncio.to_thread(run_inference, normed[None])
    ci = int(probs.argmax())
    conf = float(probs[ci])
    policy = get_policy()
    status = "recognized" if conf >= float(policy.get("threshold", 0.4)) else "uncertain"
    ms = round((time.perf_counter() - t0) * 1000, 2)
    pid = ""
    if body.session_id:
        from app.routers.session import log_prediction
        pid = log_prediction(body.session_id, f"ISL_{ci + 1:03d}", round(conf, 4), model_version())
    return JSONResponse(content={
        "success": True,
        "prediction": {"class_id": f"ISL_{ci + 1:03d}", "label": label_of(f"ISL_{ci + 1:03d}"),
                       "confidence": round(conf, 4), "prediction_id": pid},
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
