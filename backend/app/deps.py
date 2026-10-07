"""Shared deps: model registry, auth (split rule), rate limit, DB sessions (T4.1/T4.4)."""

from __future__ import annotations

import copy
import csv
import hmac
import json
import os
import time
from collections import defaultdict
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import numpy as np
from fastapi import Header, HTTPException, Request

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT / "models"

SEQ_LEN = int(os.getenv("SEQ_LEN", "45"))
FEAT_DIM = int(os.getenv("FEAT_DIM", "189"))
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
RATE_PER_MIN = int(os.getenv("RATE_PER_MIN", "60"))

# No-sign energy gate (Task 11): shared by predict.py and stream.py.
NOSIGN_ENERGY = 1e-6

_model = None
_scaler = None
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
        from app.metrics import MODEL_LOADED
        MODEL_LOADED.set(1)
    return _model


def get_scaler():
    global _scaler
    if _scaler is None:
        d = np.load(MODELS / "scaler_mvp50.npz")
        _scaler = (d["mean"].astype("float32"), d["std"].astype("float32"))
    return _scaler


def _registry_path() -> Path:
    return MODELS / "registry.json"


def _policy_path() -> Path:
    return MODELS / "EXP-2026-001-gru-full" / "policy.json"


def _file_mtime_ns(path: Path) -> int | None:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return None


_registry_mtime_ns: int | None = None
_policy_mtime_ns: int | None = None


@lru_cache(maxsize=1)
def _read_registry_cached() -> dict:
    """Underlying cached registry file read (one entry; keyed by nothing).

    Never call directly: go through read_registry(), which guards on mtime
    so on-disk edits (including direct writes outside write_registry()) are
    picked up, and returns a deepcopy so callers cannot mutate the cache.
    """
    try:
        return json.loads(_registry_path().read_text())
    except OSError:
        return {}


@lru_cache(maxsize=1)
def _read_policy_cached() -> dict:
    """Underlying cached policy file read; see _read_registry_cached."""
    try:
        return json.loads(_policy_path().read_text())
    except OSError:
        return {"threshold": 0.4, "smoothing_window": 5}


def get_policy() -> dict:
    """Return the decode policy (cached file read; deepcopy per call).

    Cached in-process; a restart picks up policy.json edits. Restarts are
    also the documented pickup path for CSV/registry edits.
    """
    global _policy_mtime_ns
    mtime = _file_mtime_ns(_policy_path())
    if mtime != _policy_mtime_ns:
        _read_policy_cached.cache_clear()
        _policy_mtime_ns = mtime
    return copy.deepcopy(_read_policy_cached())


def read_registry() -> dict:
    """Read models/registry.json ({} when the file is absent).

    Cached in-process (lru_cache); any on-disk change is picked up via an
    mtime guard, and write_registry() clears the cache explicitly on every
    write path (promote/rollback). Restart picks up CSV/registry edits.
    Returns a deepcopy so callers cannot mutate the cached entry.
    """
    global _registry_mtime_ns
    mtime = _file_mtime_ns(_registry_path())
    if mtime != _registry_mtime_ns:
        _read_registry_cached.cache_clear()
        _registry_mtime_ns = mtime
    return copy.deepcopy(_read_registry_cached())


def write_registry(reg: dict) -> None:
    """Persist the model registry (promote path; LF endings like the committed file).

    Clears the read_registry() cache (and refreshes its mtime guard) so the
    next read — e.g. GET /model right after a promote/rollback — sees the
    just-written content immediately.
    """
    global _registry_mtime_ns
    (MODELS / "registry.json").write_text(json.dumps(reg, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
    _read_registry_cached.cache_clear()
    _registry_mtime_ns = _file_mtime_ns(_registry_path())


def model_version() -> str:
    reg = read_registry()
    return (reg.get("active_model") or reg.get("model_id")
            or os.getenv("MODEL_VERSION", "SBAI-MDL-ISL-1.0.0"))


def assert_prod_secret_ok() -> None:
    """Refuse non-dev boot with the default JWT secret (called from create_app)."""
    if os.getenv("APP_ENV", "development") == "production" \
            and os.getenv("JWT_SECRET", "change-me") == "change-me":
        raise RuntimeError(
            "Refusing to start with APP_ENV=production and the default "
            "JWT_SECRET='change-me': set a strong JWT_SECRET before production boot.")


def require_auth(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Bearer token required"})
    token = authorization.split(" ", 1)[1]
    try:
        ok = hmac.compare_digest(token.encode("utf-8"), JWT_SECRET.encode("utf-8"))
    except Exception:
        ok = False
    if not ok:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Invalid token"})
    return "authenticated"


_hits: dict[tuple[str, str], list[float]] = defaultdict(list)


def _check_rate_limit(request: Request, limit: int, tier: str) -> None:
    """Shared sliding-window limiter keyed by (client IP, tier)."""
    ip = request.client.host if request.client else "unknown"
    key = (ip, tier)
    now = time.time()
    window = [t for t in _hits[key] if now - t < 60]
    _hits[key] = window
    if len(window) >= limit:
        raise HTTPException(status_code=429, detail={"code": "RATE_LIMITED", "message": "Too many requests"})
    window.append(now)


def rate_limit(request: Request, limit: int | None = None) -> None:
    """Guarded-tier limiter (predict/session/admin/...): RATE_PER_MIN per IP.

    Bucket key is (IP, "guarded"), isolated from the open tier, so hammering
    the open GETs can never 429 legitimate authed traffic (and vice versa).
    """
    limit = RATE_PER_MIN if limit is None else limit
    return _check_rate_limit(request, limit, "guarded")


def open_rate_limit(request: Request, limit: int | None = None) -> None:
    """Open-tier limiter (health/model/classes): 120/min per IP by default.

    Bucket key is (IP, "open"), isolated from the guarded tier. The caller
    (app.main) passes OPEN_RATE_PER_MIN explicitly; the default mirrors it.
    """
    limit = 120 if limit is None else limit
    return _check_rate_limit(request, limit, "open")


def reset_rate_limit() -> None:
    _hits.clear()


_engines: dict = {}


def _db_url() -> str:
    """Resolve the DB URL at call time (env honored, cached per URL)."""
    return os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'signbridge_m1.db'}")


def get_engine():
    """Return the one cached engine for the current DATABASE_URL.

    `create_all` runs once per engine (at creation), not per session.
    """
    from sqlalchemy import create_engine
    import sys
    sys.path.insert(0, str(ROOT / "backend"))
    from app.models import Base
    url = _db_url()
    eng = _engines.get(url)
    if eng is None:
        eng = create_engine(url)
        Base.metadata.create_all(eng)
        _engines[url] = eng
    return eng


@contextmanager
def get_db_session():
    """Yield a SQLAlchemy session that is always closed on exit."""
    from sqlalchemy.orm import Session
    s = Session(get_engine())
    try:
        yield s
    finally:
        s.close()


def get_db():
    """Yield SQLAlchemy session (SQLite-local, PG via DATABASE_URL).

    Kept as a thin shim for existing importers; prefer `get_db_session()`.
    """
    with get_db_session() as s:
        yield s
