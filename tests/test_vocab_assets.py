"""Vocab visual-mapping audit: 100 entries, valid images, valid CSS, label parity.

- Every class_map entry must resolve to an existing, valid JPEG in BOTH
  data/assets (backend /assets mount) and frontend/public/assets (vite dev).
- No Tailwind aspect-* utility outside the supported set may appear in
  frontend sources (aspect-4/3 and aspect-16/10 generate no CSS in
  Tailwind v3.4 and collapse image boxes to zero height).
- Every frontend dictionary class_id/label must match class_map exactly.
"""
import csv
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA_ASSETS = ROOT / "data" / "assets"
PUBLIC_ASSETS = ROOT / "frontend" / "public" / "assets"
SRC = ROOT / "frontend" / "src"

VALID_ASPECT = {"aspect-auto", "aspect-square", "aspect-video"}


def class_map():
    with (ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_100_entries_have_valid_jpegs_in_both_asset_dirs():
    rows = class_map()
    assert len(rows) == 109
    problems = []
    for r in rows:
        for base in (DATA_ASSETS, PUBLIC_ASSETS):
            p = base / f"{r['class_id']}.jpg"
            if not p.exists():
                problems.append(f"missing {p}")
                continue
            try:
                with Image.open(p) as im:
                    im.verify()
                    if im.size[0] < 64 or im.size[1] < 64:
                        problems.append(f"tiny {p}: {im.size}")
            except Exception as e:  # noqa: BLE001
                problems.append(f"unreadable {p}: {e}")
    assert not problems, "\n".join(problems)


def test_no_unsupported_aspect_utilities():
    bad = []
    for p in SRC.rglob("*.tsx"):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for m in re.findall(r"aspect-(?:\[[^\]]+\]|[\w/.-]+)", line):
                if m not in VALID_ASPECT and not m.startswith("aspect-["):
                    bad.append(f"{p.relative_to(ROOT)}:{i}: {m}")
    assert not bad, "aspect utilities with no Tailwind output:\n" + "\n".join(bad)


def test_frontend_dictionary_matches_class_map():
    rows = class_map()
    expected = {r["class_id"]: r["label"] for r in rows}
    text = (SRC / "views" / "TextToSign.tsx").read_text(encoding="utf-8")
    by_id = {}
    for _key, cid, label in re.findall(r'([a-z][\w ]*|"[a-z][\w ]*"):\s*\{\s*class_id:\s*"(ISL_\d{3})",\s*label:\s*"([^"]+)"', text):
        by_id[cid] = label
    missing = [cid for cid in expected if cid not in by_id]
    mismatched = [cid for cid, lab in by_id.items() if cid in expected and expected[cid] != lab]
    assert not missing, f"class_ids absent from frontend dictionary: {missing}"
    assert not mismatched, f"label mismatches: {[(c, by_id[c], expected[c]) for c in mismatched]}"
