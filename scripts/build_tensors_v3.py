"""V3+ tensor builder: (N,45,189) REAL tensors from ISL500 .h5 landmarks.

Reads however many rows class_map currently has (--tag names the outputs,
default 100_real). Same feature pipeline as T2.3; never touches v1 files.
"""
import argparse
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
from features.build import (
    FEAT_DIM,
    FEAT_DIM_V2,
    SEQ_LEN,
    frame_features,
    frame_features_v2,
    to_sequence,
)

RAW = ROOT / "data" / "dataset" / "raw" / "isl500" / "Landmarks" / "MediaPipe"
OUT = ROOT / "data" / "dataset" / "processed"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def gloss_of(name: str) -> str:
    g = name.split("__session")[0].split("_")[-1]
    return "" if g and g[0].isdigit() else g


def main(tag: str = "100_real", feat: str = "v1") -> None:
    assert feat in ("v1", "v2"), feat
    feat_dim = FEAT_DIM if feat == "v1" else FEAT_DIM_V2
    cmap = {}
    for r in csv.DictReader((ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8")):
        cmap[norm(r["label"])] = (r["class_id"], r["label"])
    nclass = len(cmap)
    assert nclass >= 2, f"class_map must have rows, got {nclass}"
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
            canon = canonicalize(frames)
            normed = normalize(canon)
            feats = frame_features_v2(canon, normed) if feat == "v2" else frame_features(normed)
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
    if feat == "v2":
        ref = OUT / f"tensors_{tag.split('_')[0]}_real.npz"
        assert ref.exists(), f"v1 reference npz missing: {ref}"
        R = np.load(ref)
        assert np.array_equal(R["y"], y), "y mismatch vs v1 npz — sample order/labels differ"
        assert np.array_equal(R["files"], np.array(files)), "files mismatch vs v1 npz"
        print(f"integrity guard OK vs {ref.name}", flush=True)
    np.savez_compressed(
        OUT / f"tensors_{tag}.npz", X=X, mask=M, y=y,
        signers=np.array(signers), srcs=np.array(srcs), files=np.array(files))
    # cut-rule gate
    sgn = defaultdict(set)
    for s, c in zip(signers, [list(lab2idx)[i] for i in y]):
        sgn[c].add(s)
    thin = [c for c in sorted(lab2idx) if per_class[c] < 15 or len(sgn[c]) < 10]
    meta = {"n": len(y), "classes": len(set(y.tolist())), "seq_len": SEQ_LEN,
            "feat_dim": feat_dim, "feat": feat, "skipped": skipped,
            "signers": sorted(set(signers)),
            "class_index": {c: lab2idx[c] for c in sorted(lab2idx)},
            "per_class": {c: [per_class[c], len(sgn[c])] for c in sorted(lab2idx)},
            "cut_list": thin}
    (OUT / f"tensors_{tag}.json").write_text(json.dumps(meta, indent=1))
    print("saved", OUT / f"tensors_{tag}.npz", X.shape, "skipped:", skipped, flush=True)
    print(f"classes meeting cut rule: {nclass - len(thin)}/{nclass}", flush=True)
    if thin:
        print("CUT:", thin, flush=True)
        raise SystemExit(1)
    print("TENSORS OK", flush=True)


if __name__ == "__main__":
    import argparse

    _p = argparse.ArgumentParser()
    _p.add_argument("--tag", default="100_real")
    _p.add_argument("--feat", choices=["v1", "v2"], default="v1")
    main(**vars(_p.parse_args()))
