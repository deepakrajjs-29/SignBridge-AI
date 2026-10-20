"""Motion-energy group metrics: per-class speed energy vs frozen TEST F1.

Groups the 109 classes into low/mid/high motion terciles (per-class median
mean|speed|, speeds at v1 layout 126:168) and joins per-class TEST F1 to
compare accuracy across motion regimes.

Usage: py -3 scripts/eval_group_metrics.py
Writes: Docs/eval/motion_group_metrics.json (prints a group table).
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "backend"))
from app.eval_groups import assign_groups, class_motion_energy  # noqa: E402

D = np.load(ROOT / "data/dataset/processed" / "tensors_109_real.npz")
x, y = D["X"], D["y"]

energy = class_motion_energy(x, y)
groups = assign_groups(energy, n_groups=3)

f1_by_class: dict[int, float] = {}
with open(ROOT / "Docs/eval/08_final_test_per_class.csv", newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        class_idx = int(row["class_id"].split("_")[1]) - 1
        f1_by_class[class_idx] = float(row["f1"])

group_names = {0: "low", 1: "mid", 2: "high"}
per_class = []
for c in range(len(energy)):
    per_class.append(
        {
            "class_index": c,
            "class_id": f"ISL_{c + 1:03d}",
            "motion_energy": float(energy[c]),
            "group": group_names[int(groups[c])],
            "group_index": int(groups[c]),
            "test_f1": f1_by_class.get(c),
        }
    )

summary = {}
for g in range(3):
    rows = [r for r in per_class if r["group_index"] == g]
    f1s = [r["test_f1"] for r in rows if r["test_f1"] is not None]
    summary[group_names[g]] = {
        "n_classes": len(rows),
        "mean_f1": round(float(np.mean(f1s)), 4),
        "median_f1": round(float(np.median(f1s)), 4),
    }

out = {
    "source": {
        "features": "data/dataset/processed/tensors_109_real.npz (v1, speeds 126:168, raw)",
        "per_class_f1": "Docs/eval/08_final_test_per_class.csv (frozen TEST, SBAI-MDL-ISL-4.0.0)",
        "grouping": "np.quantile(energy, [1/3, 2/3]), ties -> lower group",
    },
    "n_classes": len(energy),
    "n_groups": 3,
    "per_class": per_class,
    "groups": summary,
}
path = ROOT / "Docs/eval/motion_group_metrics.json"
path.write_text(json.dumps(out, indent=2), encoding="utf-8")

print(f"{'group':<6} {'n':>4} {'mean_f1':>9} {'median_f1':>10}")
for g in ("low", "mid", "high"):
    s = summary[g]
    print(f"{g:<6} {s['n_classes']:>4} {s['mean_f1']:>9.4f} {s['median_f1']:>10.4f}")
print(f"wrote {path}")
