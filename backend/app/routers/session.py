"""T4.2 — session lifecycle (in-memory) + DB-backed predictions; vocab list."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from prometheus_client import Counter
from pydantic import BaseModel

from app.deps import (get_db_session, label_of, model_version, rate_limit,
                      require_auth, reset_rate_limit)

logger = logging.getLogger(__name__)

# No fitting *_total/error series exists in app/metrics.py (only http/infer/
# model_loaded), so the failure counter lives here; it is still exported via
# the global registry used by GET /metrics.
PREDICTION_ERRORS_TOTAL = Counter(
    "prediction_errors_total",
    "Prediction persistence failures swallowed by best-effort log_prediction.",
)

router = APIRouter()
SESSIONS: dict[str, dict] = {}


class SessionBody(BaseModel):
    user_id: str = ""


@router.post("/session")
async def open_session(body: SessionBody, request: Request, _=Depends(require_auth)):
    sid = f"sess_{uuid.uuid4().hex[:8]}"
    SESSIONS[sid] = {"user_id": body.user_id, "created": time.time(), "predictions": []}
    return {"success": True, "session_id": sid, "request_id": getattr(request.state, "request_id", "")}


@router.delete("/session/{sid}")
async def close_session(sid: str, request: Request, _=Depends(require_auth)):
    if sid not in SESSIONS:
        return JSONResponse(status_code=404, content={
            "success": False, "error": {"code": "NOT_FOUND", "message": "unknown session", "details": {}},
            "request_id": getattr(request.state, "request_id", "")})
    del SESSIONS[sid]
    return {"success": True, "session_id": sid, "request_id": getattr(request.state, "request_id", "")}


@router.post("/session/reset")
async def reset_session(request: Request, _=Depends(require_auth)):
    SESSIONS.clear()
    reset_rate_limit()
    return {"success": True, "request_id": getattr(request.state, "request_id", "")}


@router.get("/sessions")
async def list_sessions(request: Request, _=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import RecognitionSession
    with get_db_session() as db:
        rows = db.query(RecognitionSession).all()
        live = [{"session_id": sid, **{k: v for k, v in s.items() if k != "predictions"},
                 "live_predictions": len(s.get("predictions", []))} for sid, s in SESSIONS.items()]
        known = {s["session_id"] for s in live}
        stored = [{"session_id": r.session_id, "status": r.status,
                   "created": str(r.created_at), "live_predictions": 0}
                  for r in rows if r.session_id not in known]
        return {"success": True, "sessions": live + stored,
                "request_id": getattr(request.state, "request_id", "")}


@router.get("/sessions/{sid}/predictions")
async def session_predictions(sid: str, request: Request, _=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import Prediction
    with get_db_session() as db:
        rows = db.query(Prediction).filter(Prediction.session_id == sid).all()
        if not rows and sid not in SESSIONS:
            return JSONResponse(status_code=404, content={
                "success": False, "error": {"code": "NOT_FOUND", "message": "unknown session", "details": {}},
                "request_id": getattr(request.state, "request_id", "")})
        return {"success": True, "session_id": sid,
                "predictions": [{"prediction_id": r.prediction_id, "class_id": r.class_id,
                                 "label": label_of(r.class_id),
                                  "confidence": r.confidence, "status": r.status,
                                  "created": str(r.created_at)} for r in rows],
                "request_id": getattr(request.state, "request_id", "")}


@router.delete("/history/{pid}")
async def delete_prediction(pid: str, request: Request, _=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import Feedback, Prediction
    with get_db_session() as db:
        db.query(Feedback).filter(Feedback.prediction_id == pid).delete()
        n = db.query(Prediction).filter(Prediction.prediction_id == pid).delete()
        db.commit()
        if n == 0:
            return JSONResponse(status_code=404, content={
                "success": False, "error": {"code": "NOT_FOUND", "message": "unknown prediction", "details": {}},
                "request_id": getattr(request.state, "request_id", "")})
        return {"success": True, "prediction_id": pid,
                "request_id": getattr(request.state, "request_id", "")}


def log_prediction(session_id: str, class_id: str, confidence: float, model_id: str) -> str:
    """Persist a prediction row (best-effort; returns prediction_id).

    Never raises: persistence failures are logged (logger.exception) and
    counted (PREDICTION_ERRORS_TOTAL), and the generated ``pred_*`` id is
    still returned so callers keep working. FK parent rows (session/class/
    model) are ensured before the insert so the write cannot FK-violate on
    strict databases.
    """
    pid = f"pred_{uuid.uuid4().hex[:8]}"
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from app.models import ModelVersion, Prediction, RecognitionSession, SignClass
        with get_db_session() as db:
            if session_id not in SESSIONS:
                SESSIONS[session_id] = {"user_id": "", "created": time.time(), "predictions": []}
            if db.get(RecognitionSession, session_id) is None:
                db.add(RecognitionSession(session_id=session_id, status="active"))
                db.commit()
            if db.get(SignClass, class_id) is None:
                db.add(SignClass(class_id=class_id, label=label_of(class_id)))
                db.commit()
            if db.get(ModelVersion, model_id) is None:
                db.add(ModelVersion(model_id=model_id, version=model_id))
                db.commit()
            db.add(Prediction(prediction_id=pid, session_id=session_id, class_id=class_id,
                              model_id=model_id, confidence=confidence, status="recognized"))
            db.commit()
    except Exception:
        logger.exception("log_prediction failed for session_id=%s class_id=%s", session_id, class_id)
        PREDICTION_ERRORS_TOTAL.inc()
    SESSIONS.setdefault(session_id, {}).setdefault("predictions", []).append(pid)
    return pid
