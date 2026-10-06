"""M2 — reseed `sign_assets.uri` from `data/assets/manifest.csv` and replace the
stale `model_versions` row with the `models/registry.json` values (Task 6).

M1 seeds via `Base.metadata.create_all` (`database/seed_m1.py`); this revision
applies on top of an existing DB without dropping anything by delegating to
`scripts/seed_sign_assets.seed_sign_assets`.

    py -c "import sys; sys.path.insert(0, 'database/migrations'); \
import m2_reseed_assets_model as m; m.upgrade()"
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REVISION = "m2_reseed_assets_model"


def _load_seed_fn():
    path = ROOT / "scripts" / "seed_sign_assets.py"
    spec = importlib.util.spec_from_file_location("seed_sign_assets", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["seed_sign_assets"] = mod
    spec.loader.exec_module(mod)
    return mod.seed_sign_assets


def upgrade(engine=None) -> dict:
    """Apply the reseed. Returns {"updated": ..., "missing": ...}."""
    seed_sign_assets = _load_seed_fn()
    return seed_sign_assets(ROOT / "data" / "assets" / "manifest.csv", engine=engine)


def downgrade(engine=None) -> None:
    """Reversal only: restore the legacy stub model row this migration replaces."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    sys.path.insert(0, str(ROOT / "backend"))
    from app.models import Base, ModelVersion

    import os

    if engine is None:
        url = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'signbridge_m1.db'}")
        engine = create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        for row in s.query(ModelVersion).all():
            s.delete(row)
        s.merge(
            ModelVersion(
                model_id="signbridge-lstm-v1",
                version="SBAI-MDL-ISL-1.0.0",
                model_type="lstm",
                seq_len=45,
                feat_dim=189,
                status="development",
            )
        )
        s.commit()
