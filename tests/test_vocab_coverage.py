"""Vocab↔dataset coverage gate: every class_map label must have real
landmark clips on disk (>=15 clips across >=10 signers, per cut rule).

RED (2026-10-11): 42 of ISL_051-100 have zero coverage (synthetic-only).
GREEN requires the re-scoped vocab plus the filtered ISL500 download.
"""
import csv
import os
import re
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "dataset" / "raw" / "isl500" / "Landmarks" / "MediaPipe"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def coverage():
    cov = defaultdict(int)
    users = defaultdict(set)
    if not RAW.exists():
        return cov, users
    for user_dir in sorted(os.listdir(RAW)):
        ud = RAW / user_dir
        if not ud.is_dir():
            continue
        for f in os.listdir(ud):
            if not f.endswith(".h5"):
                continue
            gloss = f.split("__session")[0].split("_")[-1]
            if gloss and not gloss[0].isdigit():
                cov[norm(gloss)] += 1
                users[norm(gloss)].add(user_dir)
    return cov, users


def test_vocab_has_real_coverage():
    rows = list(csv.DictReader((ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8")))
    assert len(rows) == 100
    cov, users = coverage()
    short = [
        f"{r['class_id']} {r['label']}: clips={cov.get(norm(r['label']), 0)} "
        f"signers={len(users.get(norm(r['label']), set()))}"
        for r in rows
        if cov.get(norm(r["label"]), 0) < 15 or len(users.get(norm(r["label"]), set())) < 10
    ]
    assert not short, "classes without real data:\n" + "\n".join(short)
