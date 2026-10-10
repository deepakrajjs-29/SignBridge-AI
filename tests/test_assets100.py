"""Task 3: 100 sign photos exist + manifest URIs filled."""

import csv
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def count_files(pattern):
    return len(glob.glob(str(ROOT / pattern)))


def read_csv(path):
    with open(ROOT / path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_100_photos_exist_and_manifest_full():
    assert count_files("data/assets/ISL_*.jpg") == 100
    rows = read_csv("data/assets/manifest.csv")
    assert len(rows) == 100 and all(r["uri"] for r in rows)
