"""Task 6 — reseed sign asset URIs from the manifest + registry-accurate model row.

Reads `data/assets/manifest.csv` (`class_id,uri,media_type`) and upserts
`sign_assets.uri` verbatim (empty stays empty -> honest `supported:false` in
`POST /api/v1/text-to-sign`), and replaces the stale `model_versions` row
with the values from `models/registry.json` so `GET /api/v1/admin/models`
returns the registry's `model_id` with `status: active`.

Usage:
    py scripts/seed_sign_assets.py [manifest_path]

No new dependencies (stdlib + sqlalchemy, already required). Creates tables
if missing but never drops anything (unlike `database/seed_m1.py`).
"""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, ModelVersion, SignAsset

REGISTRY_PATH = ROOT / "models" / "registry.json"
DEFAULT_MANIFEST = ROOT / "data" / "assets" / "manifest.csv"
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'signbridge_m1.db'}")


def load_registry(path: Path = REGISTRY_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_manifest(path: Path | str = DEFAULT_MANIFEST) -> dict[str, dict[str, str]]:
    """Return {class_id: {"uri": ..., "media_type": ...}} from the manifest CSV."""
    out: dict[str, dict[str, str]] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cid = (row.get("class_id") or "").strip()
            if not cid:
                continue
            out[cid] = {
                "uri": (row.get("uri") or "").strip(),
                "media_type": (row.get("media_type") or "").strip(),
            }
    return out


def _model_kwargs(reg: dict) -> dict:
    arch = str(reg.get("arch", ""))
    model_type = "gru" if arch.upper().startswith("GRU") else (
        "lstm" if arch.upper().startswith("LSTM") else "gru"
    )
    test = reg.get("test", {}) or {}
    return {
        "model_id": reg["model_id"],
        "version": reg.get("version", reg["model_id"]),
        "model_type": model_type,
        "seq_len": int(reg.get("seq_len", 45)),
        "feat_dim": int(reg.get("feat_dim", 189)),
        "accuracy": test.get("accuracy"),
        "macro_f1": test.get("macro_f1"),
        "artifact_uri": f"models/{reg['model_id']}.keras",
        "status": "active",
    }


def seed_sign_assets(
    manifest_path: Path | str = DEFAULT_MANIFEST,
    engine=None,
    db_url: str | None = None,
) -> dict:
    """Upsert asset URIs from the manifest + the registry model row.

    Returns {"updated": <assets matched to a manifest entry>,
             "missing": <manifest ids with no asset row + asset class_ids
                         absent from the manifest>}.
    """
    manifest = load_manifest(manifest_path)
    reg = load_registry()
    if engine is None:
        engine = create_engine(db_url or DB_URL)
    Base.metadata.create_all(engine)
    updated = 0
    missing = 0
    with Session(engine) as s:
        for class_id, entry in manifest.items():
            asset = s.query(SignAsset).filter(SignAsset.class_id == class_id).first()
            if asset is None:
                missing += 1
                continue
            asset.uri = entry["uri"]
            if entry["media_type"]:
                asset.type = entry["media_type"]
            updated += 1
        known = set(manifest)
        for asset in s.query(SignAsset).all():
            if asset.class_id not in known:
                missing += 1
        # Replace any non-registry model row (e.g. legacy signbridge-lstm-v1)
        # with the registry-accurate active row.
        for row in s.query(ModelVersion).all():
            if row.model_id != reg["model_id"]:
                s.delete(row)
        s.merge(ModelVersion(**_model_kwargs(reg)))
        s.commit()
    return {"updated": updated, "missing": missing}


def main() -> None:
    manifest = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MANIFEST
    result = seed_sign_assets(manifest)
    print(f"seed_sign_assets ok: updated={result['updated']} missing={result['missing']}")


if __name__ == "__main__":
    main()
