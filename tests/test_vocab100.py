"""Task 1: freeze 100-word vocabulary (ISL_001-100, all Dynamic)."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASS_MAP = ROOT / "data" / "dataset" / "annotations" / "class_map.csv"


def read_class_map(path=CLASS_MAP):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_class_map_100():
    return read_class_map(CLASS_MAP)


def test_class_map_has_100_dynamic():
    rows = read_class_map("data/dataset/annotations/class_map.csv")
    assert len(rows) == 100
    assert rows[50]["class_id"] == "ISL_051" and rows[50]["label"] == "Good"
    assert rows[99]["class_id"] == "ISL_100" and rows[99]["label"] == "Cold"
    assert all(r["sign_type"] == "Dynamic" for r in rows)
