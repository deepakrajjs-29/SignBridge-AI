"""T2.4 — SPLIT-1.0: deterministic signer-separated 70/15/15 split + leakage gate."""
import json
from pathlib import Path
import numpy as np

ROOT = Path("D:/Projects/SignBridge")
D = np.load(ROOT / "data/dataset/processed/tensors_mvp50.npz")
signers = D["signers"].tolist()
y = D["y"].tolist()

# deterministic: train U001-U010 (~67%), val U011-U012 (~13%), test U013-U015 (20%)
SPLIT = {"train": [f"U{i:03d}" for i in range(1, 11)],
         "val": ["U011", "U012"],
         "test": ["U013", "U014", "U015"]}
assert sum(len(v) for v in SPLIT.values()) == 15

idx = {k: [i for i, s in enumerate(signers) if s in v] for k, v in SPLIT.items()}
# leakage gate: zero signer overlap
sets = [set(v) for v in SPLIT.values()]
assert sets[0].isdisjoint(sets[1]) and sets[0].isdisjoint(sets[2]) and sets[1].isdisjoint(sets[2]), "SIGNER LEAKAGE"
assert sum(len(v) for v in idx.values()) == len(signers), "split coverage != N"

def dist(idxs):
    from collections import Counter
    c = Counter(y[i] for i in idxs)
    return {"n": len(idxs), "min_per_class": min(c.values()), "max_per_class": max(c.values()),
            "classes": len(c)}

manifest = {"split_id": "SPLIT-1.0", "rule": "signer-separated, frozen test U013-U015",
            "signers": SPLIT, "index": idx,
            "stats": {k: dist(v) for k, v in idx.items()},
            "leakage_check": "PASS (pairwise signer sets disjoint)"}
(ROOT / "data/dataset/annotations/SPLIT-1.0.json").write_text(json.dumps(
    {k: (v if k != "index" else {kk: len(vv) for kk, vv in v.items()}) for k, v in manifest.items()}, indent=1))
np.savez_compressed(ROOT / "data/dataset/processed/split_idx.npz", **{k: np.array(v) for k, v in idx.items()})
print(json.dumps(manifest["stats"], indent=1))
print("leakage:", manifest["leakage_check"], "| N =", len(signers))
