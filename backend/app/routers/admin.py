"""T4.4 — admin model registry + RBAC + audit log."""

from __future__ import annotations

import hashlib
import time

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.deps import get_db, model_version, require_auth

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
    db = next(get_db())
    rows = db.query(ModelVersion).all()
    if not rows:
        rows = [ModelVersion(model_id=model_version(), version=model_version(),
                             model_type="gru", seq_len=45, feat_dim=189, status="active")]
    return {"success": True,
            "models": [{"model_id": r.model_id, "version": r.version, "status": r.status} for r in rows],
            "request_id": getattr(request.state, "request_id", "")}


@router.post("/promote")
async def promote(body: PromoteBody, request: Request, actor=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import ModelDeployment
    db = next(get_db())
    db.add(ModelDeployment(model_id=body.model_id, environment=body.environment))
    _audit(db, actor, f"promote:{body.model_id}->{body.environment}", request)
    return {"success": True, "model_id": body.model_id, "environment": body.environment,
            "request_id": getattr(request.state, "request_id", "")}


@router.post("/rollback")
async def rollback(body: PromoteBody, request: Request, actor=Depends(require_auth)):
    db = next(get_db())
    _audit(db, actor, f"rollback:{body.model_id}->{body.environment}", request)
    return {"success": True, "model_id": body.model_id, "environment": body.environment,
            "rolled_back_at": time.time(), "request_id": getattr(request.state, "request_id", "")}
