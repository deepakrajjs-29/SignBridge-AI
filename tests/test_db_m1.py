import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, SignAsset, SignClass


def test_models_create_and_seed_shape():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(SignClass(class_id="ISL_001", label="Hello"))
        s.add(SignAsset(asset_id="asset-ISL_001", class_id="ISL_001", type="video", uri=""))
        s.commit()
        assert s.query(SignClass).count() == 1
        assert s.query(SignAsset).count() == 1
