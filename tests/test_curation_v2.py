"""Task 2: curate new-50 datasets (CURATION-v2.0)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "dataset" / "annotations" / "CURATION-v2.0.json"


def load_json(path=MANIFEST):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def test_curation_v2_counts_and_cut_rule():
    m = load_json("data/dataset/annotations/CURATION-v2.0.json")
    assert m["version"] == "CURATION-v2.0"
    assert len(m["classes"]) == 100
    for c in m["classes"]:
        if c["class_id"] not in m["cut_list"]:
            assert c["clips"] >= 15 and c["signers"] >= 10


def test_curate_v2_manifest_carries_provenance():
    m = load_json("data/dataset/annotations/CURATION-v2.0.json")
    # manifest must carry source/signer/session + checksums + source commit hashes
    assert "checksums" in m and isinstance(m["checksums"], dict)
    assert "source_commits" in m and isinstance(m["source_commits"], dict)
    for c in m["classes"]:
        assert "source" in c and "signer_ids" in c and "session_ids" in c
        assert "checksum" in c
        assert len(c["signer_ids"]) == c["signers"]


def test_curate_v2_function_contract():
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from curate_v2 import curate_v2

    out = curate_v2(str(MANIFEST))
    assert "per_class_counts" in out and "cut_list" in out
    assert len(out["per_class_counts"]) == 100
    assert out["cut_list"] == load_json(str(MANIFEST))["cut_list"]
