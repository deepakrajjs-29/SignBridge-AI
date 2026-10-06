"""T4.3 — TTS stub (501 until engine configured) + text-to-sign asset lookup."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.deps import get_db, label_of, require_auth

router = APIRouter()


class TTSBody(BaseModel):
    text: str


class T2SBody(BaseModel):
    text: str


@router.post("/tts")
async def tts(body: TTSBody, request: Request, _=Depends(require_auth)):
    return JSONResponse(status_code=501, content={
        "success": False,
        "error": {"code": "TTS_NOT_CONFIGURED",
                  "message": "Speech engine not configured (P5 wiring); text echoed for contract testing.",
                  "details": {"text": body.text[:200]}},
        "request_id": getattr(request.state, "request_id", "")})


@router.post("/text-to-sign")
async def text_to_sign(body: T2SBody, request: Request, _=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.models import SignAsset, SignClass
    words = [w.strip().lower() for w in body.text.split() if w.strip()]
    db = next(get_db())
    items, unsupported = [], []
    for w in words:
        row = db.query(SignClass).filter(SignClass.label.ilike(w)).first()
        if row is None:
            unsupported.append(w)
            continue
        asset = db.query(SignAsset).filter(SignAsset.class_id == row.class_id).first()
        items.append({"word": w, "class_id": row.class_id, "label": row.label,
                      "asset_uri": asset.uri if asset else None,
                      "supported": bool(asset and asset.uri)})
    return {"success": True, "items": items, "unsupported_words": unsupported,
            "request_id": getattr(request.state, "request_id", "")}
