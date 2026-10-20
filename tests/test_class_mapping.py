import csv
from app import deps

def test_class_map_sorted_and_aligned_with_label_of():
    with open("data/dataset/annotations/class_map.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ids = [r["class_id"] for r in rows]
    assert ids == [f"ISL_{i+1:03d}" for i in range(len(ids))]
    for r in rows[::11]:
        assert deps.label_of(r["class_id"]) == r["label"]

def test_class_list_order_matches_sorted_map():
    ids = [c["class_id"] for c in deps.class_list()]
    assert ids == [f"ISL_{i+1:03d}" for i in range(len(ids))]
