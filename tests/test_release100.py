"""Task 9: RC 100-word release gate (RED -> GREEN).

Gate: 100 classes + 100 assets + model SBAI-MDL-ISL-2.0.0 + frozen
synthetic-test acc/F1 >= 0.90. Synthetic scope: thresholds are measured on
EXP-2026-002 synthetic prototypes+noise, NOT real ISL landmarks.
"""

import csv
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def classes_count() -> int:
    with open(ROOT / "data" / "dataset" / "annotations" / "class_map.csv",
              newline="", encoding="utf-8") as f:
        return len(list(csv.DictReader(f)))


def assets_count() -> int:
    return len(glob.glob(str(ROOT / "data" / "assets" / "ISL_*.jpg")))


def model_id() -> str:
    reg = json.loads((ROOT / "models" / "registry.json").read_text(encoding="utf-8"))
    return reg.get("active_model", reg.get("model_id", ""))


def frozen_acc() -> float:
    gate = json.loads((ROOT / "models" / "SBAI-MDL-ISL-2.0.0" / "eval.json")
                      .read_text(encoding="utf-8"))
    return float(gate["measured"]["test_accuracy"])


def frozen_f1() -> float:
    gate = json.loads((ROOT / "models" / "SBAI-MDL-ISL-2.0.0" / "eval.json")
                      .read_text(encoding="utf-8"))
    return float(gate["measured"]["test_macro_f1"])


def test_release100_gates():
    assert classes_count() == 100 and assets_count() == 100
    assert model_id() == "SBAI-MDL-ISL-2.0.0"
    assert frozen_acc() >= 0.90 and frozen_f1() >= 0.90
