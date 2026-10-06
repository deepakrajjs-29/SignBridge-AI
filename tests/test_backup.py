"""Task 6 — back up the real database (sqlite file copy + postgres pg_dump).

Tmp-based; never touches the live tree or dev DB.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_backup():
    """Load scripts/backup.py as a plain module (no package import)."""
    path = ROOT / "scripts" / "backup.py"
    spec = importlib.util.spec_from_file_location("backup_mod", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["backup_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def _scratch_tree(base: Path) -> None:
    """Minimal scratch tree mimicking the backed-up artifacts."""
    (base / "models").mkdir(parents=True, exist_ok=True)
    (base / "data" / "dataset" / "annotations").mkdir(parents=True, exist_ok=True)
    (base / "docs").mkdir(parents=True, exist_ok=True)
    (base / "models" / "SBAI-MDL-ISL-1.0.0.keras").write_bytes(b"fake-keras")
    (base / "models" / "scaler_mvp50.npz").write_bytes(b"fake-scaler")
    (base / "models" / "registry.json").write_text('{"active_model": "SBAI-MDL-ISL-1.0.0"}')
    (base / "signbridge_m1.db").write_bytes(b"fake-sqlite-db")
    (base / "data" / "dataset" / "annotations" / "class_map.csv").write_text("id,label\n0,A\n")
    (base / "data" / "dataset" / "annotations" / "SPLIT-1.0.json").write_text('{"split": 1}')
    (base / "docs" / "RC_v0.5.json").write_text('{"rc": "0.5"}')


def test_sqlite_backup_still_works(tmp_path, monkeypatch):
    mod = _load_backup()
    tree = tmp_path / "tree"
    _scratch_tree(tree)
    monkeypatch.setattr(mod, "ROOT", tree)
    monkeypatch.setattr(mod, "BACKUP_BASE", tmp_path / "backups")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tree / 'signbridge_m1.db'}")

    dest = mod.backup("t6-sqlite")
    man = json.loads((dest / "manifest.json").read_text())

    assert man["db_kind"] == "sqlite"
    res = mod.restore(dest, verify_only=True)
    assert res["signbridge_m1.db"] == "HASH-OK"  # manifest HASH-OK on scratch tree
    assert all(v in ("HASH-OK", "SKIPPED-MISSING") for v in res.values())


def test_postgres_backup_invokes_pg_dump(tmp_path, monkeypatch):
    mod = _load_backup()
    tree = tmp_path / "tree"
    _scratch_tree(tree)
    monkeypatch.setattr(mod, "ROOT", tree)
    monkeypatch.setattr(mod, "BACKUP_BASE", tmp_path / "backups")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://u:pw@pg-host:5432/signbridge"
    )

    calls = {}

    class _Done:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(cmd, **kwargs):
        calls["cmd"] = list(cmd)
        out = Path(cmd[cmd.index("-f") + 1])
        out.write_bytes(b"fake-pg-dump")
        return _Done()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    dest = mod.backup("t6-pg")
    flat = " ".join(calls["cmd"])
    assert "pg_dump" in flat  # command contains pg_dump + host/db
    assert "pg-host" in flat
    assert "signbridge" in flat
    man = json.loads((dest / "manifest.json").read_text())
    assert man["db_kind"] == "postgres"
    res = mod.restore(dest, verify_only=True)
    assert res["database/postgres.dump"] == "HASH-OK"
