"""Seed sign_classes from class_map.csv + stub model version (M1). SQLite-local, PG-ready."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, ModelVersion, SignAsset, SignClass

CLASS_MAP = ROOT / "data" / "dataset" / "annotations" / "class_map.csv"
MANIFEST = ROOT / "data" / "assets" / "manifest.csv"
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'signbridge_m1.db'}")


def _apply_asset_reseed(engine) -> dict:
    """Route through the Task 6 reseed so this owning seed path cannot leave the
    stale model row or empty-URI drift behind (no drops inside)."""
    import importlib.util

    path = ROOT / "scripts" / "seed_sign_assets.py"
    spec = importlib.util.spec_from_file_location("seed_sign_assets", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.seed_sign_assets(MANIFEST, engine=engine)


def main(engine=None) -> None:
    if engine is None:
        engine = create_engine(DB_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        with CLASS_MAP.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
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
            s.merge(SignAsset(asset_id=f"asset-{r['class_id']}", class_id=r["class_id"], type="video", uri=""))
        s.merge(
            ModelVersion(
                model_id="signbridge-lstm-v1",
                version=os.getenv("MODEL_VERSION", "SBAI-MDL-ISL-1.0.0"),
                model_type="lstm",
                seq_len=45,
                feat_dim=189,
                status="development",
            )
        )
        s.commit()
    # Reseed URIs + registry-accurate model row on the same engine so a rerun
    # of this owning seed path converges instead of reintroducing the stale row.
    _apply_asset_reseed(engine)
    with Session(engine) as s:
        n_classes = s.query(SignClass).count()
        n_assets = s.query(SignAsset).count()
        n_models = s.query(ModelVersion).count()
    print(f"seed ok: classes={n_classes} assets={n_assets} models={n_models} db={DB_URL}")
    assert n_classes == 50, f"expected 50 classes, got {n_classes}"
    assert n_assets == 50, f"expected 50 assets, got {n_assets}"


if __name__ == "__main__":
    main()
