"""Filtered ISL500 landmark download for the 50 re-scoped words (v3).

Reads target stems from class_map ISL_051-100, normalizes to HF filename
form (strip non-alnum, e.g. 'Good Afternoon' -> 'Goodafternoon' resolved
against the live repo file list), and snapshot-downloads only
Landmarks/MediaPipe/*/<stem>__* . Skips files already on disk.
"""
import collections
import re
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT))

import csv

LOCAL = ROOT / "data/dataset/raw/isl500"

# HF filename stems, derived from class_map ISL_051+ labels: strip
# non-alphanumerics, then capitalize (matches HF naming: 'Good Afternoon'->
# 'Goodafternoon', verified against the live repo file list).
# Idempotent: snapshot_download skips files already on disk, and report()
# verifies every stem meets the cut rule (exit 1 otherwise).
rows = list(csv.DictReader((ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8")))
STEMS = [re.sub(r"[^A-Za-z0-9]", "", r["label"]).capitalize() for r in rows[50:]]

# Sanity: stems must match class_map ISL_051+ labels (normalized).
labels = [r["label"] for r in rows[50:]]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


mismatch = [label for label in labels if norm(label) not in {s.lower() for s in STEMS}]
assert not mismatch, f"stems out of sync with class_map: {mismatch}"


def report() -> None:
    got = collections.Counter()
    users = collections.defaultdict(set)
    mp = LOCAL / "Landmarks" / "MediaPipe"
    for u in sorted(mp.iterdir()):
        if not u.is_dir():
            continue
        for f in u.iterdir():
            if f.suffix != ".h5":
                continue
            g = f.name.split("__session")[0].split("_")[-1]
            got[g] += 1
            users[g].add(u.name)
    missing = [s for s in STEMS if got.get(s, 0) < 15 or len(users.get(s, set())) < 10]
    print(f"stems meeting cut rule: {len(STEMS) - len(missing)}/{len(STEMS)}", flush=True)
    for s in STEMS:
        print(f"  {s:15s} clips={got.get(s, 0):4d} signers={len(users.get(s, set())):2d}", flush=True)
    if missing:
        print("MISSING:", missing, flush=True)
        sys.exit(1)
    print("DOWNLOAD OK", flush=True)


def run() -> None:
    patterns = [f"Landmarks/MediaPipe/*/{s}__*" for s in STEMS]
    print(f"downloading {len(patterns)} patterns ...", flush=True)
    out = snapshot_download(
        repo_id="ISL500/ISL-DATA",
        repo_type="dataset",
        local_dir=str(LOCAL),
        allow_patterns=patterns,
    )
    print("snapshot dir:", out, flush=True)
    report()


if __name__ == "__main__":
    run()
