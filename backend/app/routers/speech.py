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


def match_phrases(text: str) -> tuple[list[str], list[str]]:
    """Longest-phrase-first match (max 3 words) against class labels.

    Returns (matched phrases in order, leftover single words).
    Matching is case-insensitive; returned phrases/words are lowercased.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.deps import class_list
    known = {str(c["label"]).lower() for c in class_list()}
    words = [w.strip().lower() for w in text.split() if w.strip()]
    matched, leftover = [], []
    i = 0
    while i < len(words):
        hit = None
        for n in (3, 2, 1):
            chunk = words[i:i + n]
            if len(chunk) != n:
                continue
            cand = " ".join(chunk)
            if cand in known:
                hit = cand
                break
        if hit is None:
            leftover.append(words[i])
            i += 1
        else:
            matched.append(hit)
            i += len(hit.split(" "))
    return matched, leftover


@router.post("/text-to-sign")
async def text_to_sign(body: T2SBody, request: Request, _=Depends(require_auth)):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.deps import class_list
    from app.models import SignAsset, SignClass
    canonical = {str(c["label"]).lower(): c["label"] for c in class_list()}
    phrases, unsupported = match_phrases(body.text)
    db = next(get_db())
    items = []
    for p in phrases:
        row = db.query(SignClass).filter(SignClass.label == canonical[p]).first()
        if row is None:
            row = db.query(SignClass).filter(SignClass.label.ilike(p)).first()
        if row is None:
            unsupported.append(p)
            continue
        asset = db.query(SignAsset).filter(SignAsset.class_id == row.class_id).first()
        items.append({"word": p, "class_id": row.class_id, "label": row.label,
                      "asset_uri": asset.uri if asset else None,
                      "supported": bool(asset and asset.uri)})
    return {"success": True, "items": items, "unsupported_words": unsupported,
            "request_id": getattr(request.state, "request_id", "")}
