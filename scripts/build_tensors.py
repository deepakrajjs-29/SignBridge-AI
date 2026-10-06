"""T2.3 — build (N,45,189) tensors from ISL500 landmark .h5 files (M2 tensor factory)."""
import csv, json, re, sys
from pathlib import Path
import numpy as np

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
from preprocessing.landmarks import canonicalize, load_h5, normalize
from features.build import frame_features, to_sequence, SEQ_LEN, FEAT_DIM

RAW = ROOT / "data" / "dataset" / "raw" / "isl500" / "Landmarks" / "MediaPipe"
OUT = ROOT / "data" / "dataset" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

cmap = {}
for r in csv.DictReader((ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8")):
    cmap[re.sub(r"[^a-z0-9]", "", r["label"].lower())] = (r["class_id"], r["label"])

X, M, y, signers, srcs, files = [], [], [], [], [], []
label_ids = sorted({c for c, _ in cmap.values()})
lab2idx = {c: i for i, c in enumerate(sorted(set(c for c, _ in [cmap[k] for k in cmap])))}
# stable idx by class_id order
lab2idx = {c: i for i, c in enumerate(sorted(lab2idx))}

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
skipped, total = 0, 0
h5files = sorted(RAW.rglob("*.h5"))
print("h5 files found:", len(h5files))
for p in h5files:
    total += 1
    word = p.name.split("__")[0]
    hit = cmap.get(norm(word))
    if not hit:
        skipped += 1
        continue
    cid, lab = hit
    try:
        frames = load_h5(str(p))
        feats = frame_features(normalize(canonicalize(frames)))
        seq, mask = to_sequence(feats)
        X.append(seq); M.append(mask); y.append(lab2idx[cid])
        m = re.match(r"ISL_DATA_USER(\d+)", p.parent.name)
        signers.append(f"U{m.group(1)}" if m else p.parent.name)
        srcs.append("isl500-landmark"); files.append(p.name)
    except Exception as e:
        skipped += 1
        if skipped < 5: print("skip", p.name, str(e)[:100])

X = np.stack(X).astype("float32"); M = np.stack(M).astype("float32")
y = np.array(y, dtype=np.int64)
np.savez_compressed(OUT / "tensors_mvp50.npz", X=X, mask=M, y=y,
                    signers=np.array(signers), srcs=np.array(srcs), files=np.array(files))
meta = {"n": len(y), "classes": len(set(y.tolist())), "seq_len": SEQ_LEN, "feat_dim": FEAT_DIM,
        "skipped": skipped, "signers": sorted(set(signers)),
        "class_index": {c: lab2idx[c] for c in sorted(lab2idx)}}
(OUT / "tensors_mvp50.json").write_text(json.dumps(meta, indent=1))
print("saved", OUT / "tensors_mvp50.npz", X.shape, "skipped:", skipped)
print(json.dumps({k: (v if k != "class_index" else f"{len(v)} classes") for k, v in meta.items()}, indent=1))
