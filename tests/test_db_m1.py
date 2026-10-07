import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, ModelVersion, SignAsset, SignClass


def _class_ids() -> list[str]:
    with (ROOT / "data" / "dataset" / "annotations" / "class_map.csv").open(
        newline="", encoding="utf-8"
    ) as f:
        return [r["class_id"] for r in csv.DictReader(f)]


def _seed_stale_state(s: Session) -> None:
    """Mimic the verified pre-fix DB: stale lstm/development row, 50 empty-URI assets."""
    for cid in _class_ids():
        s.merge(SignClass(class_id=cid, label=cid))
        s.merge(SignAsset(asset_id=f"asset-{cid}", class_id=cid, type="video", uri=""))
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


def _load_seed_fn():
    """Load seed_sign_assets from scripts/seed_sign_assets.py (plain script, no package)."""
    import importlib.util

    path = ROOT / "scripts" / "seed_sign_assets.py"
    spec = importlib.util.spec_from_file_location("seed_sign_assets", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.seed_sign_assets


def _load_seed_m1():
    """Load database/seed_m1.py (the owning seed path) as a module."""
    import importlib.util

    path = ROOT / "database" / "seed_m1.py"
    spec = importlib.util.spec_from_file_location("seed_m1", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_models_create_and_seed_shape():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(SignClass(class_id="ISL_001", label="Hello"))
        s.add(SignAsset(asset_id="asset-ISL_001", class_id="ISL_001", type="video", uri=""))
        s.commit()
        assert s.query(SignClass).count() == 1
        assert s.query(SignAsset).count() == 1


def test_admin_models_match_registry():
    """admin/models must return the registry's model_id+version with status active."""
    seed_sign_assets = _load_seed_fn()
    reg = json.loads((ROOT / "models" / "registry.json").read_text())
    expected_version = reg.get("version", reg["model_id"])
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        _seed_stale_state(s)
        result = seed_sign_assets(ROOT / "data" / "assets" / "manifest.csv", engine=engine)
        assert result["missing"] == 0
        rows = {r.model_id: r for r in s.query(ModelVersion).all()}
    assert reg["model_id"] in rows
    assert rows[reg["model_id"]].version == expected_version
    assert rows[reg["model_id"]].status == "active"
    assert "signbridge-lstm-v1" not in rows  # stale row replaced


def test_supported_flags_match_manifest():
    """supported == bool(uri) for every class; URIs equal the manifest verbatim."""
    seed_sign_assets = _load_seed_fn()
    manifest_path = ROOT / "data" / "assets" / "manifest.csv"
    with manifest_path.open(newline="", encoding="utf-8") as f:
        manifest = {r["class_id"]: r["uri"] for r in csv.DictReader(f)}
    assert len(manifest) == 50
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        _seed_stale_state(s)
        result = seed_sign_assets(manifest_path, engine=engine)
        assert result["updated"] == 50
        assert result["missing"] == 0
        assets = {a.class_id: a for a in s.query(SignAsset).all()}
    assert len(assets) == 50
    for class_id, uri in manifest.items():
        assert class_id in assets
        assert assets[class_id].uri == uri
        assert bool(assets[class_id].uri) == bool(uri)  # supported flag honesty


def test_session_is_closed_after_use(tmp_path, monkeypatch):
    """get_db_session() must close the session on context exit (spy on close)."""
    import app.deps as deps_mod

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 't4_close.db'}")
    closed = []
    with deps_mod.get_db_session() as s:
        orig_close = s.close

        def _spy():
            closed.append(True)
            return orig_close()

        s.close = _spy
        assert closed == []
    assert closed == [True]


def test_engine_reused_across_calls(tmp_path, monkeypatch):
    """get_engine() returns the same cached engine for the same URL."""
    import app.deps as deps_mod

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 't4_reuse.db'}")
    e1 = deps_mod.get_engine()
    e2 = deps_mod.get_engine()
    assert e1 is e2


def test_seed_m1_rerun_keeps_registry_row():
    """Rerunning the owning seed path (database/seed_m1.py) must not reintroduce
    the stale row or wipe URIs: registry-accurate active row survives, no stale
    row exists, and asset URIs still match the manifest verbatim."""
    seed_m1 = _load_seed_m1()
    reg = json.loads((ROOT / "models" / "registry.json").read_text())
    expected_version = reg.get("version", reg["model_id"])
    manifest_path = ROOT / "data" / "assets" / "manifest.csv"
    with manifest_path.open(newline="", encoding="utf-8") as f:
        manifest = {r["class_id"]: r["uri"] for r in csv.DictReader(f)}
    engine = create_engine("sqlite:///:memory:")
    seed_m1.main(engine=engine)  # first run through the owning seed path
    seed_m1.main(engine=engine)  # rerun must converge, not reintroduce stale state
    with Session(engine) as s:
        rows = {r.model_id: r for r in s.query(ModelVersion).all()}
        assert reg["model_id"] in rows
        assert rows[reg["model_id"]].version == expected_version
        assert rows[reg["model_id"]].status == "active"
        assert "signbridge-lstm-v1" not in rows  # stale row must not come back
        assets = {a.class_id: a for a in s.query(SignAsset).all()}
    assert len(assets) == 50
    for class_id, uri in manifest.items():
        assert assets[class_id].uri == uri


def test_version_reader_cached(monkeypatch):
    """Two read_registry()/model_version() calls -> one underlying file read (spy)."""
    import pathlib

    import app.deps as deps_mod

    reads = []
    orig = pathlib.Path.read_text

    def _count(self, *args, **kwargs):
        if self.name == "registry.json":
            reads.append(1)
        return orig(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "read_text", _count)
    deps_mod._read_registry_cached.cache_clear()
    deps_mod._registry_mtime_ns = None
    try:
        deps_mod.read_registry()
        deps_mod.model_version()
        assert len(reads) == 1, f"expected 1 registry file read, got {len(reads)}"
    finally:
        deps_mod._read_registry_cached.cache_clear()
        deps_mod._registry_mtime_ns = None
