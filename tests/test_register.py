"""Task 15: registry merge preserves deployment keys; portable script paths.

No retraining, no registry file writes here — all inputs are plain dicts and
the live ``models/registry.json`` is never touched (read-only).
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.register import build_registry

REPO_ROOT = Path(__file__).resolve().parents[1]


def _existing():
    return {
        "model_id": "SBAI-MDL-ISL-0.9.0",
        "arch": "OLD-ARCH",
        "active_model": "SBAI-MDL-ISL-1.0.0",
        "previous_model": "SBAI-MDL-ISL-0.9.0",
        "history": [
            {"model_id": "SBAI-MDL-ISL-1.0.0",
             "environment": "production", "action": "promote"},
        ],
    }


def _fresh():
    return {
        "model_id": "SBAI-MDL-ISL-2.0.0",
        "arch": "GRU128-GRU64-Dense64-Softmax50",
        "status": "Candidate",
        "seq_len": 45,
        "feat_dim": 189,
        "classes": 50,
        "sha256": "abc123",
        "export_parity_200": True,
        "test": {"accuracy": 0.91},
        "policy": {"threshold": 0.4},
        "challenger_lstm": "n/a",
        "fixes": [],
    }


def test_build_registry_preserves_deployment_keys():  # existing active/previous/history survive rebuild
    existing, fresh = _existing(), _fresh()
    merged = build_registry(existing, fresh)
    assert merged["active_model"] == "SBAI-MDL-ISL-1.0.0", merged
    assert merged["previous_model"] == "SBAI-MDL-ISL-0.9.0", merged
    assert merged["history"] == existing["history"], merged
    # training keys come from the fresh training registry, not the old one
    assert merged["model_id"] == "SBAI-MDL-ISL-2.0.0", merged
    assert merged["arch"] == "GRU128-GRU64-Dense64-Softmax50", merged
    assert merged["sha256"] == "abc123", merged
    assert merged["test"] == {"accuracy": 0.91}, merged
    assert merged["policy"] == {"threshold": 0.4}, merged


def test_build_registry_absent_deployment_keys_not_invented():
    merged = build_registry({"model_id": "OLD"}, _fresh())
    assert "active_model" not in merged, merged
    assert "previous_model" not in merged, merged
    assert "history" not in merged, merged
    assert merged["model_id"] == "SBAI-MDL-ISL-2.0.0", merged


def test_build_registry_does_not_mutate_inputs():
    existing, fresh = _existing(), _fresh()
    before_existing, before_fresh = copy.deepcopy(existing), copy.deepcopy(fresh)
    merged = build_registry(existing, fresh)
    assert existing == before_existing
    assert fresh == before_fresh
    assert merged["history"] is not existing["history"]  # deep-copied, not aliased
    merged["history"].append({"model_id": "X"})
    assert existing["history"] == before_existing["history"]


def test_scripts_use_portable_root():
    for name in ("scripts/register.py", "scripts/e2e_10sign.py", "scripts/smoke_prod.py"):
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        assert "ROOT = Path(__file__).resolve().parents[1]" in text, name
        assert "D:/Projects/SignBridge" not in text, name
        assert "D:\\Projects\\SignBridge" not in text, name
