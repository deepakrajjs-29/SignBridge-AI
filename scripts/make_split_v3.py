"""V3+ split: deterministic signer-separated 70/15/15 split (train U001-U010,
val U011-U012, test U013-U015, zero signer overlap gate). --tag selects the
tensor/split artifacts, --split-id names the manifest (defaults preserve
the 100-class SPLIT-3.0 outputs).
"""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path("D:/Projects/SignBridge")


def main(tag: str = "100_real", split_id: str = "SPLIT-3.0") -> None:
    D = np.load(ROOT / "data/dataset/processed" / f"tensors_{tag}.npz")
    signers = D["signers"].tolist()
    y = D["y"].tolist()

    SPLIT = {"train": [f"U{i:03d}" for i in range(1, 11)],
             "val": ["U011", "U012"],
             "test": ["U013", "U014", "U015"]}
    assert sum(len(v) for v in SPLIT.values()) == 15

    idx = {k: [i for i, s in enumerate(signers) if s in v] for k, v in SPLIT.items()}
    sets = [set(v) for v in SPLIT.values()]
    assert sets[0].isdisjoint(sets[1]) and sets[0].isdisjoint(sets[2]) and sets[1].isdisjoint(sets[2]), "SIGNER LEAKAGE"
    assert sum(len(v) for v in idx.values()) == len(signers), "split coverage != N"


    def dist(idxs):
        from collections import Counter
        c = Counter(y[i] for i in idxs)
        return {"n": len(idxs), "min_per_class": min(c.values()), "max_per_class": max(c.values()),
                "classes": len(c)}


    manifest = {"split_id": split_id, "rule": "signer-separated, frozen test U013-U015",
                "signers": SPLIT, "index": idx,
                "stats": {k: dist(v) for k, v in idx.items()},
                "leakage_check": "PASS (pairwise signer sets disjoint)"}
    (ROOT / "data/dataset/annotations" / f"{split_id}.json").write_text(json.dumps(
        {k: (v if k != "index" else {kk: len(vv) for kk, vv in v.items()}) for k, v in manifest.items()}, indent=1))
    tag_suffix = tag.split("_")[0]
    np.savez_compressed(ROOT / "data/dataset/processed" / f"split_idx_{tag_suffix}.npz",
                        **{k: np.array(v) for k, v in idx.items()})
    print(json.dumps(manifest["stats"], indent=1))
    print("leakage:", manifest["leakage_check"], "| N =", len(signers))


if __name__ == "__main__":
    _p = argparse.ArgumentParser()
    _p.add_argument("--tag", default="100_real")
    _p.add_argument("--split-id", default="SPLIT-3.0")
    _a = _p.parse_args()
    main(tag=_a.tag, split_id=_a.__dict__["split_id"])
