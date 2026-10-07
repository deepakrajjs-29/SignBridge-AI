"""Task 18 — minimal feedback submit endpoint (dead Feedback schema)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.deps import get_db_session, require_auth

router = APIRouter()


class FeedbackBody(BaseModel):
    prediction_id: str
    actual_class_id: str | None = None
    rating: int | None = None


@router.post("/feedback")
async def submit_feedback(body: FeedbackBody, request: Request, _=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import Feedback, Prediction
    with get_db_session() as db:
        if db.get(Prediction, body.prediction_id) is None:
            return JSONResponse(status_code=404, content={
                "success": False,
                "error": {"code": "NOT_FOUND", "message": "unknown prediction", "details": {}},
                "request_id": getattr(request.state, "request_id", "")})
        fb = Feedback(prediction_id=body.prediction_id,
                      actual_class_id=body.actual_class_id, rating=body.rating)
        db.add(fb)
        db.commit()
        fid = fb.feedback_id
    return {"success": True, "feedback_id": fid,
            "request_id": getattr(request.state, "request_id", "")}
