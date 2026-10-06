"""Shared deps: model registry, auth (split rule), rate limit, DB sessions (T4.1/T4.4)."""

from __future__ import annotations

import csv
import json
import os
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from fastapi import Header, HTTPException, Request

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "models"

SEQ_LEN = int(os.getenv("SEQ_LEN", "45"))
FEAT_DIM = int(os.getenv("FEAT_DIM", "189"))
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
RATE_PER_MIN = int(os.getenv("RATE_PER_MIN", "60"))

_model = None
_scaler = None
_policy = {"threshold": 0.4, "smoothing_window": 5}
_classes: list[dict] = []


def class_list() -> list[dict]:
    global _classes
    if not _classes:
        with (ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                _classes.append({"class_id": r["class_id"], "label": r["label"],
                                 "sign_type": r.get("sign_type", "Dynamic")})
    return _classes


def label_of(class_id: str) -> str:
    for c in class_list():
        if c["class_id"] == class_id:
            return c["label"]
    return class_id


def get_model():
    global _model
    if _model is None:
        import tensorflow as tf
        _model = tf.keras.models.load_model(MODELS / "SBAI-MDL-ISL-1.0.0.keras")
    return _model


def get_scaler():
    global _scaler
    if _scaler is None:
        d = np.load(MODELS / "scaler_mvp50.npz")
        _scaler = (d["mean"].astype("float32"), d["std"].astype("float32"))
    return _scaler


def get_policy() -> dict:
    global _policy
    p = MODELS / "EXP-2026-001-gru-full" / "policy.json"
    if p.exists():
        _policy = json.loads(p.read_text())
    return _policy


def model_version() -> str:
    try:
        reg = json.loads((MODELS / "registry.json").read_text())
        return reg.get("model_id", os.getenv("MODEL_VERSION", "SBAI-MDL-ISL-1.0.0"))
    except OSError:
        return os.getenv("MODEL_VERSION", "SBAI-MDL-ISL-1.0.0")


def require_auth(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Bearer token required"})
    if authorization.split(" ", 1)[1] != JWT_SECRET:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Invalid token"})
    return "authenticated"


_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit(request: Request, limit: int | None = None) -> None:
    limit = RATE_PER_MIN if limit is None else limit
    key = request.client.host if request.client else "unknown"
    now = time.time()
    window = [t for t in _hits[key] if now - t < 60]
    _hits[key] = window
    if len(window) >= limit:
        raise HTTPException(status_code=429, detail={"code": "RATE_LIMITED", "message": "Too many requests"})
    window.append(now)


def reset_rate_limit() -> None:
    _hits.clear()


def get_db():
    """Yield SQLAlchemy session (SQLite-local, PG via DATABASE_URL)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    import sys
    sys.path.insert(0, str(ROOT / "backend"))
    from app.models import Base
    url = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'signbridge_m1.db'}")
    eng = create_engine(url)
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        yield s
