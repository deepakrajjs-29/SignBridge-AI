"""V3 — render one REAL landmark-skeleton keyframe per re-scoped word (ISL_051-100).

Source: the downloaded ISL500 MediaPipe .h5 files (same clips the 3.0.0
model trains on). Takes the temporal middle frame of the first clean clip
per stem, wrist-normalizes via the ai pipeline, projects x/y to a 640px
canvas and draws both-hand skeletons. Files are honest landmark
visualizations (not camera photos) and are labeled as such in the UI copy.
Overwrites the synthetic placeholders for ISL_051-100 only.
"""
import csv
import re
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
sys.path.insert(0, str(ROOT / "scripts"))
from preprocessing.landmarks import canonicalize, load_h5, normalize  # noqa: E402
from download_isl500_v3 import STEMS  # noqa: E402

LAND = ROOT / "data" / "dataset" / "raw" / "isl500" / "Landmarks" / "MediaPipe"
ASSETS = ROOT / "data" / "assets"

EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
         (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15),
         (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)]


def render(frames) -> np.ndarray:
    """frames: [T][2][21][3] raw -> 640x640 BGR skeleton image."""
    seq = normalize(canonicalize(frames))
    mid = seq[len(seq) // 2]
    img = np.full((640, 640, 3), 18, dtype=np.uint8)
    colors = [(0, 200, 255), (255, 170, 0)]
    for h, hand in enumerate(mid):
        xs = [p[0] for p in hand]
        ys = [p[1] for p in hand]
        lo_x, hi_x = min(xs), max(xs)
        lo_y, hi_y = min(ys), max(ys)
        span = max(hi_x - lo_x, hi_y - lo_y, 1e-6)
        pts = [((p[0] - lo_x) / span, (p[1] - lo_y) / span) for p in hand]
        ox = 80 + h * 260
        px = [(int(ox + x * 220), int(60 + y * 220)) for x, y in pts]
        for a, b in EDGES:
            cv2.line(img, px[a], px[b], colors[h], 3, cv2.LINE_AA)
        for x, y in px:
            cv2.circle(img, (x, y), 6, (240, 240, 240), -1, cv2.LINE_AA)
    cv2.putText(img, "landmark visualization", (18, 622),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2, cv2.LINE_AA)
    return img


def main() -> None:
    rows = list(csv.DictReader((ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8")))
    assert len(rows) >= 100
    stem2cid = {s.lower(): r["class_id"] for s, r in zip(STEMS, rows[50:])}
    pick: dict[str, Path] = {}
    for u in sorted(LAND.iterdir()):
        if not u.is_dir():
            continue
        for f in sorted(u.iterdir()):
            if f.suffix != ".h5":
                continue
            g = f.name.split("__session")[0].split("_")[-1]
            if g in STEMS and g not in pick and re.fullmatch(r"[A-Za-z]+__session\d+__clip\d+\.h5", f.name):
                pick[g] = f
    missing = [s for s in STEMS if s not in pick]
    if missing:
        print("NO H5 FOR:", missing, flush=True)
        sys.exit(1)
    for s in STEMS:
        frames = load_h5(str(pick[s]))
        img = render(frames)
        out = ASSETS / f"{stem2cid[s.lower()]}.jpg"
        cv2.imwrite(str(out), img, [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(f"{stem2cid[s.lower()]} {s:15s} <- {pick[s].parent.name}/{pick[s].name}", flush=True)
    print("PHOTOS OK", flush=True)


if __name__ == "__main__":
    main()
