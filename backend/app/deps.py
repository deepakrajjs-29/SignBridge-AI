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
_model_for: str | None = None
_scaler = None
_scaler_for: str | None = None
_classes: list[dict] = []


def _asset_status_map() -> dict[str, str]:
    """class_id -> reference_status from data/assets/reference_status.csv (optional)."""
    path = ROOT / "data/assets/reference_status.csv"
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cid = (r.get("class_id") or "").strip()
            st = (r.get("status") or "").strip()
            if cid and st:
                out[cid] = st
    return out


def class_list() -> list[dict]:
    if not _classes:
        status_map = _asset_status_map()
        with (ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                _classes.append({
                    "class_id": r["class_id"],
                    "label": r["label"],
                    "gloss": r.get("gloss", r["label"].upper()),
                    "sign_type": r.get("sign_type", "Dynamic"),
                    "meaning": r.get("meaning", ""),
                    "handedness": r.get("handedness", "Both"),
                    "asset_uri": f"/assets/{r['class_id']}.jpg",
                    "asset_status": status_map.get(r["class_id"], "placeholder"),
                })
    return _classes



def label_of(class_id: str) -> str:
    for c in class_list():
        if c["class_id"] == class_id:
            return c["label"]
    return class_id


ENSEMBLE_MODELS = frozenset({"SBAI-MDL-ISL-3.0.0", "SBAI-MDL-ISL-4.0.0"})


def uses_ensemble() -> bool:
    """True when the active model is served as an LSTM+GRU+mirror ensemble."""
    return model_version() in ENSEMBLE_MODELS


def _active_keras_path() -> Path:
    """Artifact path for the registry-active model.

    4.0.0 = REAL 109-class winner; 3.0.0 = REAL 100-class winner (both served
    as ensembles — see get_ensemble); 2.0.0 = synthetic Softmax100 (kept, not
    served once 3.0.0+ is active); else 1.0.0 GRU.
    """
    if model_version() == "SBAI-MDL-ISL-4.0.0":
        return MODELS / "SBAI-MDL-ISL-4.0.0.keras"
    if model_version() == "SBAI-MDL-ISL-3.0.0":
        return MODELS / "SBAI-MDL-ISL-3.0.0.keras"
    if model_version() == "SBAI-MDL-ISL-2.0.0":
        return MODELS / "SBAI-MDL-ISL-2.0.0" / "SBAI-LSTM-100.keras"
    return MODELS / "SBAI-MDL-ISL-1.0.0.keras"


def _active_scaler_path() -> Path:
    if model_version() == "SBAI-MDL-ISL-4.0.0":
        return MODELS / "scaler_109_real.npz"
    if model_version() == "SBAI-MDL-ISL-3.0.0":
        return MODELS / "scaler_100_real.npz"
    if model_version() == "SBAI-MDL-ISL-2.0.0":
        return MODELS / "SBAI-MDL-ISL-2.0.0" / "scaler_100.npz"
    return MODELS / "scaler_mvp50.npz"


def get_model():
    global _model, _model_for
    want = model_version()
    if _model is None or _model_for != want:
        import tensorflow as tf
        _model = tf.keras.models.load_model(_active_keras_path())
        _model_for = want
        from app.metrics import MODEL_LOADED
        MODEL_LOADED.set(1)
    return _model


def get_scaler():
    global _scaler, _scaler_for
    want = model_version()
    if _scaler is None or _scaler_for != want:
        d = np.load(_active_scaler_path())
        _scaler = (d["mean"].astype("float32"), d["std"].astype("float32"))
        _scaler_for = want
    return _scaler


def mirror_features(X: np.ndarray) -> np.ndarray:
    """Exact x-mirror in 189-dim feature space (identical to train_v3 aug).

    Applied to SCALED windows (training augmented scaled features).
    Distances/speeds/magnitudes are mirror-invariant; x-coords negate;
    bbox min/max x swap. Involution: mirror(mirror(x)) == x.
    """
    M = X.copy()
    C = M[:, :, :126].reshape((-1, SEQ_LEN, 2, 21, 3))
    C[..., 0] *= -1
    for h in (0, 1):
        b = 168 + h * 10
        mnx, mxx = M[:, :, b].copy(), M[:, :, b + 3].copy()
        M[:, :, b], M[:, :, b + 3] = -mxx, -mnx
        M[:, :, b + 6] *= -1
    return M


_ensemble = None
_ensemble_for: str | None = None


def get_ensemble():
    """Cached (lstm, gru) winner pair for the active ensemble model."""
    global _ensemble, _ensemble_for
    want = model_version()
    if _ensemble is None or _ensemble_for != want:
        import tensorflow as tf

        lstm_path = MODELS / f"{want}_lstm.keras"
        gru_path = MODELS / f"{want}_gru.keras"
        if not lstm_path.exists() or not gru_path.exists():
            raise FileNotFoundError(f"{want} ensemble weights absent")
        _ensemble = (
            tf.keras.models.load_model(lstm_path),
            tf.keras.models.load_model(gru_path),
        )
        _ensemble_for = want
        from app.metrics import MODEL_LOADED

        MODEL_LOADED.set(1)
    return _ensemble


def infer_ensemble(batch: np.ndarray) -> np.ndarray:
    """Mean(LSTM, GRU, mirror-TTA) probs for a (N,45,189) SCALED batch.

    Batches [x, mirror(x)] per model: 2 predict calls total. Returns (N,C).
    """
    lstm, gru = get_ensemble()
    aug = np.concatenate([batch, mirror_features(batch)], axis=0)
    pl = lstm.predict(aug, verbose=0)
    pg = gru.predict(aug, verbose=0)
    n = batch.shape[0]
    return ((pl[:n] + pl[n:] + pg[:n] + pg[n:]) / 4).astype("float32")


def _registry_path() -> Path:
    return MODELS / "registry.json"


def _policy_path() -> Path:
    if model_version() in ENSEMBLE_MODELS:
        return MODELS / model_version() / "policy.json"
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


def _calibration_path() -> Path:
    return MODELS / model_version() / "calibration.json"


_calibration_mtime_ns: int | None = None


@lru_cache(maxsize=1)
def _read_calibration_cached() -> dict:
    """Underlying cached calibration file read; see _read_registry_cached."""
    try:
        return json.loads(_calibration_path().read_text())
    except OSError:
        return {"temperature": 1.0}


def get_calibration() -> dict:
    """Return the temperature-scaling calibration (cached; deepcopy per call).

    File absent/unreadable -> identity {"temperature": 1.0}. mtime-guarded
    cache exactly like get_policy(), so calibrate_v4.py rewrites are picked
    up without a restart.
    """
    global _calibration_mtime_ns
    mtime = _file_mtime_ns(_calibration_path())
    if mtime != _calibration_mtime_ns:
        _read_calibration_cached.cache_clear()
        _calibration_mtime_ns = mtime
    return copy.deepcopy(_read_calibration_cached())


def calibrate_probs(probs: np.ndarray) -> np.ndarray:
    """Temperature-scale class probabilities along the last axis.

    T == 1.0 returns the input unchanged (identity). T > 1 flattens the
    distribution toward uniform; T < 1 sharpens it. Output sums to 1.
    """
    T = float(get_calibration().get("temperature", 1.0))
    if T == 1.0:
        return probs
    logp = np.log(np.clip(probs, 1e-12, 1.0)) / T
    e = np.exp(logp - np.max(logp, axis=-1, keepdims=True))
    return (e / np.sum(e, axis=-1, keepdims=True)).astype("float32")


def preprocess_window(frames: np.ndarray) -> np.ndarray | None:
    """Raw (T,189) client rows -> scaled (45,189) float32, or None = No-Sign.

    Exactly predict.py's historical post-envelope pipeline, now shared with
    the WS `window` branch:
    1) resample/pad to SEQ_LEN (linspace when T >= SEQ_LEN, repeat-pad below)
    2) No-Sign energy gate on the WINDOWED rows, PRE-normalization
       (post-norm the shipped scaler maps blanks to max abs ~= 0.67, so a
       post-norm gate could never fire for blank input)
    3) scale with the active scaler
    Callers own their envelope checks (REST 422/413/404, WS INVALID_INPUT):
    shape, finiteness and T <= 600 are validated before this is called.

    A motion-energy static head/tail trim (M13 P1) was TRIED here and
    rejected by its VAL gate — see Docs/M13_ACCURACY_CALIBRATION.md §4.2
    (full_sign 0.835 -> 0.768): the training distribution includes
    clip-internal slow frames, so trimming the resample span skews serve
    inputs off the training manifold. Do not re-add without a new idea
    that passes the same gate.
    """
    arr = np.asarray(frames, dtype="float32")
    if arr.size == 0:
        return None  # defensive: envelopes normally reject this first
    if len(arr) >= SEQ_LEN:
        idx = np.linspace(0, len(arr) - 1, SEQ_LEN).astype(int)
        seq = arr[idx]
    else:
        seq = np.concatenate([arr, np.tile(arr[-1:], (SEQ_LEN - len(arr), 1))])
    if float(np.abs(seq).max()) < NOSIGN_ENERGY:
        return None
    mu, sd = get_scaler()
    return ((seq - mu.reshape(189)) / sd.reshape(189)).astype("float32")


def make_windows(seq_scaled: np.ndarray, k: int) -> np.ndarray:
    """TTA view set for one scaled (45,189) window -> (k',45,189), k' in {1,3}.

    k == 3 -> the three fixed crops full [0:45], early [0:39], late [6:45],
    each resampled to exactly SEQ_LEN rows via linspace over its own length.
    k == 1 (or any value other than 3, documented fallback) -> seq[None],
    i.e. numerically identical to the pre-TTA path.
    """
    if k != 3:
        return np.asarray(seq_scaled, dtype="float32")[None]
    crops = (seq_scaled[0:45], seq_scaled[0:39], seq_scaled[6:45])
    out = []
    for c in crops:
        idx = np.linspace(0, len(c) - 1, SEQ_LEN).astype(int)
        out.append(c[idx])
    return np.stack(out).astype("float32")


def recognize_probs(seq_scaled: np.ndarray, windows: int = 1) -> np.ndarray:
    """Calibrated (45,189) SCALED window -> (C,) class probabilities.

    windows == 3 applies test-time augmentation: the three make_windows()
    views run through the model and their RAW outputs are averaged BEFORE a
    single calibration step (calibrating each view first would change
    semantics for T != 1). windows == 1 is bit-identical to the pre-TTA path.
    Ensemble models flow through infer_ensemble; a non-ensemble active model
    uses one get_model().predict pass per window.
    """
    mk = make_windows(seq_scaled, windows)
    if uses_ensemble():
        raw = infer_ensemble(mk).mean(axis=0)
    else:
        raw = np.mean([get_model().predict(w[None], verbose=0)[0] for w in mk], axis=0)
    return calibrate_probs(np.asarray(raw, dtype="float32"))


def recognize_probs_batch(X_scaled: np.ndarray, windows: int = 1, chunk: int = 512) -> np.ndarray:
    """Calibrated probs for an (N,45,189) SCALED batch -> (N,C).

    Row-equivalent to calling recognize_probs on every row with the same
    `windows` (calibration is elementwise so chunking never changes the
    result). With windows > 1 the stacked views are laid out row-major —
    row0's windows first — so the mean-reduction restores per-row order.
    """
    if not uses_ensemble():
        return np.stack([recognize_probs(x, windows) for x in X_scaled]).astype("float32")
    chunks = []
    for s in range(0, len(X_scaled), chunk):
        part = X_scaled[s:s + chunk]
        if windows == 1:
            chunks.append(infer_ensemble(part))
        else:
            mk = np.concatenate([make_windows(x, windows) for x in part], axis=0)
            raw = infer_ensemble(mk)
            kk = mk.shape[0] // len(part)
            chunks.append(raw.reshape(len(part), kk, -1).mean(axis=1))
    probs = np.concatenate(chunks, axis=0).astype("float32")
    return calibrate_probs(probs)


def decision_status(conf: float, policy: dict) -> str:
    """Three-state decision for a calibrated confidence.

    "recognized"  -> conf >= accept threshold (committable)
    "provisional" -> prov <= conf < accept (display-only, plausible)
    "uncertain"   -> below prov (display-only, untrustworthy)

    Missing provisional_threshold collapses the band onto the accept
    threshold (two-state legacy behavior: recognized vs uncertain).
    """
    acc = float(policy.get("accept_threshold", policy.get("threshold", 0.4)))
    prov = min(float(policy.get("provisional_threshold", acc)), acc)
    if conf >= acc:
        return "recognized"
    if conf >= prov:
        return "provisional"
    return "uncertain"


def top_k_alternatives(probs: np.ndarray, k: int = 4) -> list[dict]:
    """Real model top-k candidates (including the argmax primary).

    Returns up to k entries of {class_id, label, confidence} sorted by
    calibrated probability descending. Never invents labels or scores.
    """
    if probs is None or len(probs) == 0:
        return []
    kk = max(1, min(int(k), len(probs)))
    idx = np.argsort(probs)[::-1][:kk]
    out: list[dict] = []
    for i in idx:
        cid = f"ISL_{int(i) + 1:03d}"
        out.append({"class_id": cid, "label": label_of(cid),
                    "confidence": round(float(probs[int(i)]), 4)})
    return out


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
