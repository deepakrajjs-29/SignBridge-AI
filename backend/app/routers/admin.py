"""T4.4 — admin model registry + RBAC + audit log."""

from __future__ import annotations

import hashlib
import time

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.deps import get_db_session, model_version, read_registry, require_auth, write_registry

router = APIRouter(prefix="/admin")


def _audit(db, actor: str, action: str, request: Request) -> None:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import AuditLog
    ip = request.client.host if request.client else ""
    db.add(AuditLog(actor=actor, action=action,
                    ip_hash=hashlib.sha256(ip.encode()).hexdigest()[:32]))
    db.commit()


class PromoteBody(BaseModel):
    model_id: str
    environment: str = "production"


@router.get("/models")
async def list_models(request: Request, _=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import ModelVersion
    with get_db_session() as db:
        rows = db.query(ModelVersion).all()
        if not rows:
            rows = [ModelVersion(model_id=model_version(), version=model_version(),
                                 model_type="gru", seq_len=45, feat_dim=189, status="active")]
        return {"success": True,
                "models": [{"model_id": r.model_id, "version": r.version, "status": r.status} for r in rows],
                "request_id": getattr(request.state, "request_id", "")}


def _known_model_ids() -> set[str]:
    """Model ids promote may point at: on-disk ``models/*.keras`` stems plus registry-history ids."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.deps import MODELS
    known = {p.stem for p in MODELS.glob("*.keras")}
    hist = read_registry().get("history")
    if isinstance(hist, list):
        for h in hist:
            if isinstance(h, dict) and h.get("model_id"):
                known.add(str(h["model_id"]))
    return known


@router.post("/promote")
async def promote(body: PromoteBody, request: Request, actor=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import ModelDeployment
    from fastapi.responses import JSONResponse
    if body.model_id not in _known_model_ids():
        return JSONResponse(status_code=422, content={
            "success": False,
            "error": {"code": "UNKNOWN_MODEL",
                      "message": f"unknown model_id: {body.model_id}",
                      "details": {"model_id": body.model_id}},
            "request_id": getattr(request.state, "request_id", "")})
    with get_db_session() as db:
        db.add(ModelDeployment(model_id=body.model_id, environment=body.environment))
        reg = read_registry()
        reg["previous_model"] = reg.get("active_model", reg.get("model_id"))
        reg["active_model"] = body.model_id
        reg["model_id"] = body.model_id
        if isinstance(reg.get("history"), list):
            reg["history"].append({"model_id": body.model_id,
                                   "environment": body.environment, "action": "promote"})
        write_registry(reg)
        _audit(db, actor, f"promote:{body.model_id}->{body.environment}", request)
        return {"success": True, "model_id": body.model_id, "environment": body.environment,
                "request_id": getattr(request.state, "request_id", "")}


@router.post("/rollback")
async def rollback(body: PromoteBody, request: Request, actor=Depends(require_auth)):
    from fastapi.responses import JSONResponse
    reg = read_registry()
    previous = reg.get("previous_model")
    if not previous:
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": {"code": "NO_ROLLBACK_STATE",
                      "message": "no previous model to roll back to",
                      "details": {}},
            "request_id": getattr(request.state, "request_id", "")})
    current = reg.get("active_model", reg.get("model_id"))
    reg["previous_model"] = current
    reg["active_model"] = previous
    reg["model_id"] = previous
    if isinstance(reg.get("history"), list):
        reg["history"].append({"model_id": previous,
                               "environment": body.environment, "action": "rollback"})
    write_registry(reg)
    with get_db_session() as db:
        _audit(db, actor, f"rollback:{previous}->{body.environment}", request)
        return {"success": True, "model_id": previous, "environment": body.environment,
                "rolled_back_at": time.time(), "request_id": getattr(request.state, "request_id", "")}
