"""V3 — download ISL500 raw videos for the 50 re-scoped words (photo source).

One clip per word per user max is NOT enforceable via patterns, so this
fetches Videos/*/<stem>__* for all users; extract_photos_v3.py then keeps a
single mid-frame JPEG per word and this snapshot may be pruned afterwards.
"""
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT))
from scripts.download_isl500_v3 import STEMS  # noqa: E402  (single source of stems)

LOCAL = ROOT / "data" / "dataset" / "raw" / "isl500"
patterns = [f"Videos/*/{s}__*" for s in STEMS]
print(f"downloading {len(patterns)} video patterns ...", flush=True)
out = snapshot_download(
    repo_id="ISL500/ISL-DATA",
    repo_type="dataset",
    local_dir=str(LOCAL),
    allow_patterns=patterns,
)
print("snapshot dir:", out, flush=True)

import collections

got = collections.Counter()
mp = LOCAL / "Videos"
for u in sorted(mp.iterdir()):
    if not u.is_dir():
        continue
    for f in u.iterdir():
        if f.suffix == ".mp4":
            got[f.name.split("__")[0]] += 1
for s in STEMS:
    print(f"  {s:15s} videos={got.get(s, 0):3d}", flush=True)
missing = [s for s in STEMS if got.get(s, 0) == 0]
if missing:
    print("MISSING VIDEOS:", missing, flush=True)
    sys.exit(1)
print("VIDEOS OK", flush=True)
