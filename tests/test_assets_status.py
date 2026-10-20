"""Asset reference coverage: 109 classes, manifest, status file, no shared blank IDs presented as unique."""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def _rows(path: Path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_manifest_and_class_map_cover_109():
    classes = _rows(ROOT / "data/dataset/annotations/class_map.csv")
    manifest = _rows(ROOT / "data/assets/manifest.csv")
    status = _rows(ROOT / "data/assets/reference_status.csv")
    assert len(classes) == 109
    assert len(manifest) == 109
    assert len(status) == 109
    assert {r["class_id"] for r in classes} == {r["class_id"] for r in status}
    assert all(r["uri"] for r in manifest)


def test_all_class_images_exist_on_disk():
    classes = _rows(ROOT / "data/dataset/annotations/class_map.csv")
    missing = []
    for r in classes:
        p = ROOT / "frontend/public/assets" / f"{r['class_id']}.jpg"
        if not p.exists() or p.stat().st_size == 0:
            missing.append(r["class_id"])
    assert missing == []


def test_needs_verified_ids_are_documented():
    status = _rows(ROOT / "data/assets/reference_status.csv")
    flagged = {r["class_id"] for r in status if r["status"] == "needs_verified_reference"}
    # The eight known byte-identical near-blank renders.
    assert flagged == {
        "ISL_053", "ISL_063", "ISL_065", "ISL_069",
        "ISL_071", "ISL_080", "ISL_081", "ISL_108",
    }


def test_flagged_images_still_exist_on_disk():
    """Flagged files still exist on disk (UI hides them); status drives UX."""
    status = _rows(ROOT / "data/assets/reference_status.csv")
    for r in status:
        if r["status"] != "needs_verified_reference":
            continue
        p = ROOT / "frontend/public/assets" / f"{r['class_id']}.jpg"
        assert p.exists()


def test_backend_class_list_includes_asset_status():
    from app.deps import class_list

    classes = class_list()
    assert len(classes) == 109
    assert all("asset_status" in c for c in classes)
    flagged = {c["class_id"] for c in classes if c["asset_status"] == "needs_verified_reference"}
    assert "ISL_053" in flagged
    assert all(c["asset_uri"].startswith("/assets/") for c in classes)
    assert classes[0]["label"] == "Hello"
    assert classes[-1]["class_id"] == "ISL_109"
