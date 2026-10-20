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


def test_class_map_has_109_dynamic():
    rows = read_class_map("data/dataset/annotations/class_map.csv")
    assert len(rows) == 109
    assert rows[0]["class_id"] == "ISL_001" and rows[0]["label"] == "Hello"
    assert rows[49]["class_id"] == "ISL_050" and rows[49]["label"] == "Bus"
    assert rows[50]["class_id"] == "ISL_051" and rows[50]["label"] == "Good"
    assert rows[99]["class_id"] == "ISL_100" and rows[99]["label"] == "Cold"
    assert rows[100]["class_id"] == "ISL_101" and rows[100]["label"] == "Library"
    assert rows[108]["class_id"] == "ISL_109" and rows[108]["label"] == "Manager"
    assert all(r["sign_type"] == "Dynamic" for r in rows)
