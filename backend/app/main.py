"""SignBridge AI backend — Phase 4 full API (M4). Split auth: open
GET /health|/model|/classes; Bearer on predict/session/tts/admin."""

from __future__ import annotations

import os
import time
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.deps import assert_prod_secret_ok, class_list, model_version, rate_limit
from app.metrics import HTTP_5XX_TOTAL, HTTP_REQUESTS_TOTAL, exposition
from app.routers import admin, feedback, predict, session as session_router, speech, stream

APP_NAME = "signbridge-ai"
SEQ_LEN = int(os.getenv("SEQ_LEN", "45"))
FEAT_DIM = int(os.getenv("FEAT_DIM", "189"))
OPEN_RATE_PER_MIN = 120


def open_rate_limit(request: Request) -> None:
    """Throttle for the open GETs (health/model/classes): 120/min/IP via the shared limiter."""
    return rate_limit(request, limit=OPEN_RATE_PER_MIN)


def error_envelope(request: Request, code: str, message: str, status: int = 400, details: dict | None = None):
    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "error": {"code": code, "message": message, "details": details or {}},
            "request_id": getattr(request.state, "request_id", ""),
        },
    )


def create_app() -> FastAPI:
    assert_prod_secret_ok()
    app = FastAPI(title=APP_NAME, version="0.2.0")

    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:3000").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, dict):
            code = detail.get("code", f"HTTP_{exc.status_code}")
            message = detail.get("message", str(detail))
            details = detail.get("details", {})
        else:
            code = f"HTTP_{exc.status_code}"
            message = str(detail) if detail else f"HTTP {exc.status_code} error"
            details = {}
        return error_envelope(request, code, message, exc.status_code, details)

    @app.middleware("http")
    async def request_id_mw(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        t0 = time.perf_counter()
        try:
            resp = await call_next(request)
        except Exception:
            return error_envelope(request, "INTERNAL", "Unhandled error", 500)
        resp.headers["X-Request-ID"] = request.state.request_id
        resp.headers["X-Process-Time-Ms"] = str(round((time.perf_counter() - t0) * 1000, 2))
        return resp

    @app.middleware("http")
    async def metrics_mw(request: Request, call_next):
        # Added after request_id_mw so this is the outer wrapper: 500s produced
        # by the inner handler are still recorded. /metrics itself is excluded
        # to avoid scrape feedback loops.
        resp = await call_next(request)
        path = request.url.path
        if path != "/metrics":
            HTTP_REQUESTS_TOTAL.labels(path=path, code=str(resp.status_code)).inc()
            if resp.status_code >= 500:
                HTTP_5XX_TOTAL.inc()
        return resp

    @app.middleware("http")
    async def api_log_mw(request: Request, call_next):
        # Task 18: sampled ApiLog insert ({request_id, path, status_code}).
        # Added after request_id_mw/metrics_mw so this is the outermost wrapper:
        # the response path runs after the inner middlewares, so request_id
        # already exists. Never alters the response: insert failures are
        # swallowed after a best-effort attempt (stderr line at most).
        resp = await call_next(request)
        try:
            try:
                rate = float(os.getenv("SAMPLE_RATE", "1.0"))
            except ValueError:
                rate = 1.0
            import random
            if random.random() < rate:
                from app.deps import get_db_session
                from app.models import ApiLog
                with get_db_session() as db:
                    db.add(ApiLog(request_id=getattr(request.state, "request_id", "") or "",
                                  path=request.url.path, status_code=resp.status_code))
                    db.commit()
        except Exception as exc:
            import sys
            print(f"api_log insert failed: {exc}", file=sys.stderr)
        return resp

    @app.get("/metrics")
    async def metrics():
        # No auth by design: Prometheus scrapes this unauthenticated.
        data, content_type = exposition()
        return Response(content=data, media_type=content_type)

    @app.get("/health")
    async def health(request: Request, _=Depends(open_rate_limit)):
        return {"success": True, "status": "ok", "model_version": model_version(),
                "request_id": request.state.request_id}

    @app.get("/api/v1/model")
    async def model_info(request: Request, _=Depends(open_rate_limit)):
        return {"success": True,
                "model": {"model_id": "signbridge-gru-v1", "model_version": model_version(),
                          "seq_len": SEQ_LEN, "feat_dim": FEAT_DIM,
                          "architecture": "GRU128-GRU64-Dense64-Softmax50 (Candidate, M3 debt)"},
                "request_id": request.state.request_id}

    @app.get("/api/v1/classes")
    async def classes(request: Request, _=Depends(open_rate_limit)):
        cls = class_list()
        return {"success": True, "count": len(cls), "classes": cls,
                "request_id": request.state.request_id}

    app.include_router(predict.router, prefix="/api/v1", tags=["predict"])
    app.include_router(session_router.router, prefix="/api/v1", tags=["session"])
    app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
    app.include_router(speech.router, prefix="/api/v1", tags=["speech"])
    app.include_router(stream.router, prefix="/api/v1", tags=["stream"])
    app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
    return app


app = create_app()
