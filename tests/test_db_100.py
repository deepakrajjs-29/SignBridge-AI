"""Task 4: DB holds 100 sign_classes + 100 photo sign_assets (from class_map/manifest)."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "database" / "migrations"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, SignAsset, SignClass

import m3_seed_100


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    m3_seed_100.seed_100(engine)
    with Session(engine) as s:
        yield s


def test_db_has_100_classes_and_assets(db):
    assert db.query(SignClass).count() == 100
    assert db.query(SignAsset).filter(SignAsset.type == "photo").count() == 100
