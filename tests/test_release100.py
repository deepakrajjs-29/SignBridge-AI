"""3.0.0 real-data release gate (replaces the synthetic 2.0.0 gate).

Gate: 100 classes + 100 assets + active model SBAI-MDL-ISL-3.0.0, with
frozen-test numbers pinned to the MEASURED EXP-2026-003 values
(acc 0.7721 / macro-F1 0.7664, n=3326, signer-independent U013-U015).

M-gate debt (honest): 0.7721/0.7664 is below the 0.90/0.90 release gates.
This test is a regression tripwire on measured values, not a gate-pass
claim. See Docs/M10_GATE_100REAL.md.
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


def _registered_300() -> dict:
    reg = json.loads((ROOT / "models" / "registry.json").read_text(encoding="utf-8"))
    return reg["models"]["SBAI-MDL-ISL-3.0.0"]


def frozen_acc() -> float:
    return float(_registered_300()["measured_test_acc"])


def frozen_f1() -> float:
    return float(_registered_300()["measured_test_f1"])


def test_release100_gates():
    assert classes_count() == 100 and assets_count() == 100
    assert model_id() == "SBAI-MDL-ISL-3.0.0"
    # Pinned measured values (LSTM winner, frozen signer-independent test).
    assert frozen_acc() == 0.7721 and frozen_f1() == 0.7664
