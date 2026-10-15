"""V3 — build (N,45,189) REAL tensors for 100 classes from ISL500 .h5 landmarks.

Same feature pipeline as T2.3 (canonicalize/normalize/frame_features/
to_sequence from ai/); differences vs build_tensors.py:
- reads the 100-row class_map (v3 re-scope),
- gloss from the LAST underscore segment (handles HF mirror prefixes),
- (user,session,clip) dedup preferring clean filenames,
- writes tensors_100_real.npz + tensors_100_real.json, never touches v1 files.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
from preprocessing.landmarks import canonicalize, load_h5, normalize
from features.build import frame_features, to_sequence, SEQ_LEN, FEAT_DIM

RAW = ROOT / "data" / "dataset" / "raw" / "isl500" / "Landmarks" / "MediaPipe"
OUT = ROOT / "data" / "dataset" / "processed"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def gloss_of(name: str) -> str:
    g = name.split("__session")[0].split("_")[-1]
    return "" if g and g[0].isdigit() else g


def main() -> None:
    cmap = {}
    for r in csv.DictReader((ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8")):
        cmap[norm(r["label"])] = (r["class_id"], r["label"])
    assert len(cmap) == 100, f"class_map must have 100 rows, got {len(cmap)}"
    lab2idx = {c: i for i, c in enumerate(sorted({c for c, _ in cmap.values()}))}

    # Every filename is a unique clip: (user,session,clip) numbers repeat
    # across DIFFERENT glosses (per-batch numbering), and junk-prefixed
    # mirror names carry distinct sessions/clips. Verified 2026-10-11: zero
    # clean+junk twins, zero cross-dir filename repeats. No dedup applied.
    h5files = sorted(RAW.rglob("*.h5"))
    print("h5 files found:", len(h5files), flush=True)
    items = []  # (user, path, cid)
    for p in h5files:
        hit = cmap.get(norm(gloss_of(p.name)))
        if not hit:
            continue
        cid, _ = hit
        items.append((p.parent.name, p, cid))
    items.sort(key=lambda t: (t[0], t[1].name))
    print(f"clips selected: {len(items)}", flush=True)

    X, M, y, signers, srcs, files = [], [], [], [], [], []
    skipped = 0
    per_class: Counter = Counter()
    for user, p, cid in items:
        mu = re.match(r"ISL_DATA_USER(\d+)", user)
        signer = f"U{mu.group(1)}" if mu else user
        try:
            frames = load_h5(str(p))
            feats = frame_features(normalize(canonicalize(frames)))
            seq, mask = to_sequence(feats)
        except Exception as e:
            skipped += 1
            if skipped < 5:
                print("skip", p.name, str(e)[:100], flush=True)
            continue
        X.append(seq)
        M.append(mask)
        y.append(lab2idx[cid])
        signers.append(signer)
        srcs.append("isl500-landmark")
        files.append(p.name)
        per_class[cid] += 1
    X = np.stack(X).astype("float32")
    M = np.stack(M).astype("float32")
    y = np.array(y, dtype=np.int64)
    np.savez_compressed(
        OUT / "tensors_100_real.npz", X=X, mask=M, y=y,
        signers=np.array(signers), srcs=np.array(srcs), files=np.array(files))
    # cut-rule gate
    sgn = defaultdict(set)
    for s, c in zip(signers, [list(lab2idx)[i] for i in y]):
        sgn[c].add(s)
    thin = [c for c in sorted(lab2idx) if per_class[c] < 15 or len(sgn[c]) < 10]
    meta = {"n": len(y), "classes": len(set(y.tolist())), "seq_len": SEQ_LEN,
            "feat_dim": FEAT_DIM, "skipped": skipped,
            "signers": sorted(set(signers)),
            "class_index": {c: lab2idx[c] for c in sorted(lab2idx)},
            "per_class": {c: [per_class[c], len(sgn[c])] for c in sorted(lab2idx)},
            "cut_list": thin}
    (OUT / "tensors_100_real.json").write_text(json.dumps(meta, indent=1))
    print("saved", OUT / "tensors_100_real.npz", X.shape, "skipped:", skipped, flush=True)
    print("classes meeting cut rule:", 100 - len(thin), "/100", flush=True)
    if thin:
        print("CUT:", thin, flush=True)
        raise SystemExit(1)
    print("TENSORS OK", flush=True)


if __name__ == "__main__":
    main()
