"""M3 — seed 100 `sign_classes` from class_map.csv + 100 `sign_assets` type=photo.

Upserts 100 `sign_classes` from `data/dataset/annotations/class_map.csv`
(label UNIQUE) and inserts 100 `sign_assets` (type="photo", uri from
`data/assets/manifest.csv`, FK class_id). Idempotent via `Session.merge`.

Down downgrades back to the 50-word M1 shape (ISL_001-050 only).

Usage:
    py -c "import sys; sys.path.insert(0, 'database/migrations'); \
import m3_seed_100 as m; m.upgrade()"
"""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, SignAsset, SignClass

REVISION = "m3_seed_100"
CLASS_MAP = ROOT / "data" / "dataset" / "annotations" / "class_map.csv"
MANIFEST = ROOT / "data" / "assets" / "manifest.csv"
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'signbridge_m1.db'}")
KEEP_50 = [f"ISL_{i:03d}" for i in range(1, 51)]


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def seed_100(engine=None) -> tuple[int, int]:
    """Upsert 100 sign_classes + 100 photo sign_assets. Returns (n_classes, n_photo_assets)."""
    if engine is None:
        engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    class_rows = _read_csv(CLASS_MAP)
    manifest_rows = _read_csv(MANIFEST)
    with Session(engine) as s:
        for r in class_rows:
            s.merge(
                SignClass(
                    class_id=r["class_id"],
                    label=r["label"],
                    gloss=r.get("gloss", ""),
                    sign_type=r.get("sign_type", "Dynamic"),
                    meaning=r.get("meaning", ""),
                    handedness=r.get("handedness", "Both"),
                )
            )
        for r in manifest_rows:
            cid = (r.get("class_id") or "").strip()
            uri = (r.get("uri") or "").strip()
            if not cid:
                continue
            s.merge(SignAsset(asset_id=f"asset-{cid}-photo", class_id=cid, type="photo", uri=uri))
        s.commit()
        n_classes = s.query(SignClass).count()
        n_photos = s.query(SignAsset).filter(SignAsset.type == "photo").count()
    return n_classes, n_photos


def upgrade(engine=None) -> dict:
    n_classes, n_photos = seed_100(engine)
    assert n_classes == 100, f"expected 100 classes, got {n_classes}"
    assert n_photos == 100, f"expected 100 photo assets, got {n_photos}"
    return {"classes": n_classes, "photo_assets": n_photos}


def downgrade(engine=None) -> dict:
    """Drop back to the 50-word M1 shape: keep ISL_001-050, remove ISL_051-100 + their assets."""
    if engine is None:
        engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        for asset in s.query(SignAsset).all():
            if asset.class_id not in KEEP_50:
                s.delete(asset)
        for cls in s.query(SignClass).all():
            if cls.class_id not in KEEP_50:
                s.delete(cls)
        s.commit()
        n_classes = s.query(SignClass).count()
        n_photos = s.query(SignAsset).filter(SignAsset.type == "photo").count()
    return {"classes": n_classes, "photo_assets": n_photos}


def main(engine=None) -> None:
    result = upgrade(engine)
    print(f"m3_seed_100 ok: classes={result['classes']} photo_assets={result['photo_assets']}")


if __name__ == "__main__":
    main()
