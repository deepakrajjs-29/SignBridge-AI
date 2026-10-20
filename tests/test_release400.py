"""4.0.0 real-data release gate (supersedes the 3.0.0 gate).

Gate: 109 classes + 109 assets + active model SBAI-MDL-ISL-4.0.0, with
frozen-test numbers pinned to the MEASURED ensemble values
(acc 0.8129 / macro-F1 0.8079, n=3629, signer-independent U013-U015).

3.0.0 values (0.8109/0.8062, n=3326) live in git history + Docs/M10_GATE_100REAL.md.
M-gate debt (honest): single-model 0.8057/0.8012 is below the 0.90/0.90 release
gates. This test is a regression tripwire on measured values, not a gate-pass
claim. See Docs/M11_GATE_109REAL.md.
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


def _registered_400() -> dict:
    reg = json.loads((ROOT / "models" / "registry.json").read_text(encoding="utf-8"))
    return reg["models"]["SBAI-MDL-ISL-4.0.0"]


def frozen_acc() -> float:
    return float(_registered_400()["measured_test_acc"])


def frozen_f1() -> float:
    return float(_registered_400()["measured_test_f1"])


def test_release400_gates():
    assert classes_count() == 109 and assets_count() == 109
    assert model_id() == "SBAI-MDL-ISL-4.0.0"
    # Pinned measured values (deployed ensemble, frozen signer-independent test).
    assert frozen_acc() == 0.8129 and frozen_f1() == 0.8079
