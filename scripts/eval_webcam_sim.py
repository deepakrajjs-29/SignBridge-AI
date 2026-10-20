"""Offline webcam-capture replay on frozen-split h5 clips (no camera needed).

Scores the capture-window semantics that drove the reported 20-30% real-world
accuracy, using raw MediaPipe h5 clips from the chosen split (val or the frozen
test split) and the ACTIVE backend ensemble (same weights + scaler as
POST /api/v1/predict):

  full_sign        whole clip                       target of the new 3.5 s capture
  idle_realistic   +1 s static head + 1.5 s tail    new capture with reaction/idle delay
  old_45_center    centered contiguous 45 frames    old ~0.75 s capture window
  old_rafdup       45 rAF ticks over 23 cam frames  old loop reprocessing 30 fps at 60 Hz

`--split test` (default) preserves the original M12 frozen-test behavior; use
`--split val` for any gate/replay work before the single Task 8 test touch.

Usage: py -3 scripts/eval_webcam_sim.py [--split val|test] [--n 1500] [--thr 0.60] [--seed 11]
"""
import argparse
import glob
import re
import sys
from pathlib import Path

import numpy as np

P = argparse.ArgumentParser()
P.add_argument("--split", choices=["val", "test"], default="test")
P.add_argument("--n", type=int, default=1500)
P.add_argument("--thr", type=float, default=0.60)
P.add_argument("--seed", type=int, default=11)
A = P.parse_args()

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
sys.path.insert(0, str(ROOT / "backend"))
from preprocessing.landmarks import canonicalize, normalize, load_h5  # noqa: E402
from features.build import frame_features, to_sequence  # noqa: E402
from app import deps  # noqa: E402

D = np.load(ROOT / "data/dataset/processed" / "tensors_109_real.npz")
S = np.load(ROOT / "data/dataset/processed" / "split_idx_109.npz")
idx_split, files, y = S[A.split], D["files"], D["y"]
path_of = {
    re.split(r"[\\/]", p)[-1]: p
    for p in glob.glob(
        str(ROOT / "data/dataset/raw/isl500/Landmarks/MediaPipe/**/*.h5"),
        recursive=True,
    )
}
idx = np.random.default_rng(A.seed).choice(
    idx_split, min(A.n, len(idx_split)), replace=False
)
mu, sd = deps.get_scaler()


def _center(f, n):
    start = max((len(f) - n) // 2, 0)
    return f[start : start + n]


conds = {
    "full_sign": lambda f: f,
    "idle_realistic": lambda f: np.concatenate(
        [np.repeat(f[:1], 30, 0), f, np.repeat(f[-1:], 45, 0)], 0
    ),
    "old_45_center": lambda f: _center(f, 45),
    "old_rafdup": lambda f: np.repeat(_center(f, 23), 2, axis=0),
}

for name, fn in conds.items():
    rows, labels = [], []
    for i in idx:
        p = path_of.get(str(files[i]))
        if not p:
            continue
        try:
            f = load_h5(p)
        except Exception:
            continue
        try:
            rows.append(to_sequence(frame_features(normalize(canonicalize(fn(f)))))[0])
            labels.append(int(y[i]))
        except Exception:
            pass
    X = np.stack(rows).astype("float32")
    Xs = ((X - mu) / sd).astype("float32")
    probs = deps.recognize_probs_batch(Xs)
    pred, conf, yt = probs.argmax(1), probs.max(1), np.array(labels)
    ok = conf >= A.thr
    acc = float((pred == yt).mean())
    acc_ok = float((pred[ok] == yt[ok]).mean()) if ok.any() else 0.0
    vis = float(((pred == yt) & ok).mean())
    print(
        f"{name:16s} n={len(yt):4d} acc={acc:.3f} accept@{A.thr:.2f}={ok.mean():.3f} "
        f"acc|accept={acc_ok:.3f} visible_correct={vis:.3f}",
        flush=True,
    )
