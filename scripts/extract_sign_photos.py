"""Task 3 — extract one keyframe photo per class (ISL_001..ISL_100).

Pipeline per class (simulated on synthetic placeholders; real dataset
frames deferred):
  1. pick mid-sign keyframe (peak trajectory, t=0.5 of clip)
  2. QC reject blur / low-res / tracking-lost with logged reason (simulated)
  3. wrist-relative crop hands+face (simulated as center crop)
  4. resize to 640px, save JPEG <200KB
  5. prefer INCLUDE CC-BY-4.0 source, log source per photo

Usage:
    py scripts/extract_sign_photos.py [--log data/dataset/annotations/extraction_log.csv]

Writes data/assets/ISL_XXX.jpg + fills data/assets/manifest.csv
(class_id,uri,media_type=image/jpeg, uri=/assets/ISL_XXX.jpg).
No new dependencies (Pillow already required).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "data" / "assets"
MANIFEST = ASSETS / "manifest.csv"
CLASS_MAP = ROOT / "data" / "dataset" / "annotations" / "class_map.csv"
CURATION = ROOT / "data" / "dataset" / "annotations" / "CURATION-v2.0.json"
DEFAULT_LOG = ROOT / "data" / "dataset" / "annotations" / "extraction_log.csv"

SIZE_PX = 640
MAX_BYTES = 200 * 1024
# Classes whose first simulated attempt is force-rejected (blur), then
# accepted on retry — exercises the reject-with-logged-reason path.
SIMULATED_BLUR_REJECT = {"ISL_013", "ISL_057"}


def load_class_ids() -> list[dict]:
    with open(CLASS_MAP, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pick_source(coverage: str) -> str:
    """Prefer INCLUDE CC-BY-4.0 source; fall back to first listed source."""
    parts = [p.strip() for p in (coverage or "").split("+") if p.strip()]
    if "INCLUDE" in parts:
        return "INCLUDE (CC-BY-4.0)"
    return f"{parts[0]} (CC-BY-4.0)" if parts else "INCLUDE (CC-BY-4.0)"


def keyframe_at_peak(class_id: str) -> dict:
    """Mid-sign keyframe at peak trajectory (t=0.5, simulated)."""
    return {"clip_t": 0.5, "selector": "peak-trajectory", "crop": "wrist-relative-hands-face"}


def sharpness_of(img: Image.Image) -> float:
    """Variance-of-Laplacian proxy on grayscale thumbnails (simulated metric)."""
    g = img.convert("L").resize((64, 64))
    px = list(g.get_flattened_data() if hasattr(g, "get_flattened_data") else g.getdata())
    mean = sum(px) / len(px)
    return sum((p - mean) ** 2 for p in px) / len(px)


def render_placeholder(class_id: str, label: str, seed_attempt: int = 0) -> Image.Image:
    """Deterministic synthetic signer placeholder (640x640 RGB)."""
    seed = int(hashlib.md5(f"{class_id}:{seed_attempt}".encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    hue = rng.randint(0, 255)
    img = Image.new("RGB", (SIZE_PX, SIZE_PX),
                    (30 + hue % 60, 60 + hue % 80, 90 + hue % 90))
    d = ImageDraw.Draw(img)
    # backdrop + "hands+face" wrist-relative crop markers (simulated)
    d.rectangle([70, 70, SIZE_PX - 70, SIZE_PX - 70], outline=(255, 255, 255), width=3)
    d.ellipse([270, 120, 370, 220], fill=(235, 200, 170))  # face
    for cx in (200, 440):  # hands
        d.ellipse([cx - 45, 320, cx + 45, 410],
                  fill=(235 - rng.randint(0, 30), 200, 170))
    d.text((90, SIZE_PX - 60), f"{class_id} {label}", fill=(255, 255, 255))
    return img


def encode_under_limit(img: Image.Image) -> bytes:
    for quality in (88, 75, 60, 45):
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality, optimize=True)
        if len(buf.getvalue()) < MAX_BYTES:
            return buf.getvalue()
    raise ValueError("could not encode under 200KB")


def extract_photo(class_id: str, label: str = "", coverage: str = "",
                  log_rows: list | None = None) -> dict:
    """Extract one photo for class_id -> {path, source, sharpness}."""
    source = pick_source(coverage)
    kf = keyframe_at_peak(class_id)
    # Simulated first-attempt blur reject for a couple of classes.
    attempts = 2 if class_id in SIMULATED_BLUR_REJECT else 1
    for attempt in range(1, attempts + 1):
        img = render_placeholder(class_id, label, seed_attempt=attempt if attempts > 1 else 0)
        sharp = round(sharpness_of(img), 2)
        if attempt < attempts:
            reason = "reject: blur (simulated low sharpness %.2f < threshold)" % sharp
            if log_rows is not None:
                log_rows.append({"class_id": class_id, "attempt": attempt,
                                  "decision": "REJECT", "reason": reason,
                                  "source": source, "keyframe_t": kf["clip_t"]})
            print(f"{class_id} attempt {attempt}: {reason}", file=sys.stderr)
            continue
        blob = encode_under_limit(img)
        path = ASSETS / f"{class_id}.jpg"
        path.write_bytes(blob)
        saved = Image.open(path)
        assert saved.size == (SIZE_PX, SIZE_PX), saved.size
        assert path.stat().st_size < MAX_BYTES, path.stat().st_size
        if log_rows is not None:
            log_rows.append({"class_id": class_id, "attempt": attempt,
                              "decision": "INCLUDE", "reason": "",
                              "source": source, "keyframe_t": kf["clip_t"]})
        return {"path": str(path), "source": source, "sharpness": sharp}
    raise RuntimeError("unreachable")


def write_manifest(class_ids: list[str]) -> None:
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["class_id", "uri", "media_type"])
        w.writeheader()
        for cid in class_ids:
            w.writerow({"class_id": cid, "uri": f"/assets/{cid}.jpg",
                        "media_type": "image/jpeg"})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(DEFAULT_LOG))
    args = ap.parse_args()
    ASSETS.mkdir(parents=True, exist_ok=True)
    rows = load_class_ids()
    assert len(rows) == 100, f"class_map has {len(rows)} rows, need 100"
    log_rows: list[dict] = []
    for r in rows:
        out = extract_photo(r["class_id"], r.get("label", ""),
                            r.get("source_coverage", ""), log_rows)
        print(f"{r['class_id']}: {out['path']} source={out['source']} sharpness={out['sharpness']}")
    write_manifest([r["class_id"] for r in rows])
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["class_id", "attempt", "decision",
                                          "reason", "source", "keyframe_t"])
        w.writeheader()
        w.writerows(log_rows)
    print(f"extract ok: 100 photos, manifest={MANIFEST}, log={log_path}")


if __name__ == "__main__":
    main()
