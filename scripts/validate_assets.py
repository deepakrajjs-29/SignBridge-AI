"""Task 3 — validate 100 extracted sign photos + manifest coverage.

Checks: 100 files data/assets/ISL_*.jpg, each 640px JPEG <200KB;
manifest.csv has 100 rows with uri=/assets/ISL_XXX.jpg and
media_type=image/jpeg.

Usage: py scripts/validate_assets.py (exit 0 ok, 1 fail).
"""

from __future__ import annotations

import csv
import glob
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "data" / "assets"
MANIFEST = ASSETS / "manifest.csv"


def main() -> int:
    errors: list[str] = []
    files = sorted(glob.glob(str(ASSETS / "ISL_*.jpg")))
    if len(files) != 100:
        errors.append(f"photo count {len(files)} != 100")
    for p in files:
        size = Path(p).stat().st_size
        if size >= 200 * 1024:
            errors.append(f"{Path(p).name}: {size} bytes >= 200KB")
        try:
            with Image.open(p) as im:
                if im.size != (640, 640):
                    errors.append(f"{Path(p).name}: size {im.size} != (640, 640)")
                if im.format != "JPEG":
                    errors.append(f"{Path(p).name}: format {im.format} != JPEG")
        except Exception as e:  # noqa: BLE001
            errors.append(f"{Path(p).name}: unreadable ({e})")
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 100:
        errors.append(f"manifest rows {len(rows)} != 100")
    for r in rows:
        cid = r.get("class_id", "")
        if r.get("uri") != f"/assets/{cid}.jpg":
            errors.append(f"{cid}: bad uri {r.get('uri')!r}")
        if r.get("media_type") != "image/jpeg":
            errors.append(f"{cid}: bad media_type {r.get('media_type')!r}")
    covered = {Path(p).stem for p in files}
    for r in rows:
        if r.get("class_id") not in covered:
            errors.append(f"{r.get('class_id')}: missing photo file")
    if errors:
        print("validate_assets FAIL:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("validate_assets ok: 100/100 coverage, all 640px JPEG <200KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
