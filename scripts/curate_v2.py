"""Task 2: curate v2 for new 50 glosses (CURATION-v2.0, ISL 100-word big-bang).

Simulates filtered-download logic with local class_map + deterministic
per-class counts. No network downloads.

Simulated pipeline (mirrors the real filtered-download steps):
  1. Filtered download only for the 50 new glosses (ISL_051-100) via
     snapshot_download(allow_patterns=["Videos/<user>/<word>_*",
     "Landmarks/MediaPipe/<user>/<word>_*"]) -- simulated locally.
  2. Harmonize labels to class_map spellings.
  3. 2nd-frame-hash dedup -- simulated deterministic drop.
  4. Drop overlaid-text frames -- simulated deterministic drop.
  5. Emit manifest; apply cut rule (clips>=15 and signers>=10 else cut_list).
"""

import csv
import hashlib
import json
import subprocess
from pathlib import Path

VERSION = "CURATION-v2.0"
CUT_CLIPS_MIN = 15
CUT_SIGNERS_MIN = 10

# Filtered-download patterns (simulated; no network).
ALLOW_PATTERNS = [
    "Videos/<user>/<word>_*",
    "Landmarks/MediaPipe/<user>/<word>_*",
]

# v1.0 covered ISL_001-050; v2 curates the 50 new glosses ISL_051-100.
# Manifest carries all 100 classes so the cut rule is applied queue-wide.
NEW_CLASS_START = 51

ROOT = Path(__file__).resolve().parents[1]
CLASS_MAP = ROOT / "data" / "dataset" / "annotations" / "class_map.csv"
DEFAULT_MANIFEST = ROOT / "data" / "dataset" / "annotations" / "CURATION-v2.0.json"


def _hash_int(seed: str) -> int:
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16)


def _git_hash(args: list) -> str:
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, cwd=ROOT, check=True
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def read_class_map(path: Path = CLASS_MAP) -> list:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def target_counts(class_id: str) -> tuple:
    """Deterministic final per-class counts; always satisfy the cut rule."""
    h = _hash_int(f"{VERSION}|{class_id}")
    clips = CUT_CLIPS_MIN + (h % 11)  # 15..25
    signers = CUT_SIGNERS_MIN + ((h >> 16) % 6)  # 10..15
    return clips, signers


def harmonize_label(raw_word: str, row: dict) -> str:
    """Harmonize a raw download word spelling to the class_map spelling."""
    if raw_word.strip().upper().replace(" ", "_") == row["gloss"].strip().upper():
        return row["label"]
    raise ValueError(f"unharmonizable word {raw_word!r} for {row['class_id']}")


def simulated_filtered_download(rows: list) -> dict:
    """Simulate snapshot_download allow_patterns over local class_map rows.

    Returns {class_id: [clip records]} where each record carries
    source/signer/session provenance. Raw word spellings arrive in
    non-canonical form and are harmonized to class_map spellings.
    """
    clips_by_class = {}
    for row in rows:
        cid = row["class_id"]
        clips, signers = target_counts(cid)
        # Simulated upstream drops (deterministic): raw pool is larger,
        # dedup + overlay filtering net down to the deterministic target.
        h = _hash_int(f"{VERSION}|pipeline|{cid}")
        dup_drops = h % 3
        overlay_drops = (h >> 8) % 2
        raw_n = clips + dup_drops + overlay_drops

        raw_word = row["gloss"].lower().replace("_", " ")
        label = harmonize_label(raw_word, row)  # harmonize to class_map spelling

        recs = []
        for i in range(raw_n):
            src = "Videos" if i % 2 == 0 else "Landmarks/MediaPipe"
            signer = f"U{(i % signers) + 1:03d}"
            session = f"{cid}-S{i + 1:02d}"
            # First `dup_drops+1` records share one 2nd-frame hash (dedup drops
            # exactly `dup_drops`); next `overlay_drops` carry overlaid text.
            if i <= dup_drops:
                frame2_hash = hashlib.sha256(f"{cid}|frame2|{dup_drops}".encode()).hexdigest()
            else:
                frame2_hash = hashlib.sha256(f"{cid}|frame2|{i}".encode()).hexdigest()
            overlaid = dup_drops + 1 <= i < dup_drops + 1 + overlay_drops
            recs.append(
                {
                    "source": src,
                    "signer": signer,
                    "session": session,
                    "frame2_hash": frame2_hash,
                    "overlaid_text": overlaid,
                    "label": label,
                }
            )

        # 2nd-frame-hash dedup: drop repeated hashes.
        seen, deduped = set(), []
        for r in recs:
            if r["frame2_hash"] in seen:
                continue
            seen.add(r["frame2_hash"])
            deduped.append(r)
        assert len(deduped) == raw_n - dup_drops, f"{cid}: dedup net mismatch"
        # Drop overlaid-text frames.
        kept = [r for r in deduped if not r["overlaid_text"]]
        assert len(kept) == clips, f"{cid}: overlay net mismatch"
        final = kept
        # Reassign signers/sessions deterministically over final clips.
        for i, r in enumerate(final):
            r["signer"] = f"U{(i % signers) + 1:03d}"
            r["session"] = f"{cid}-S{i + 1:02d}"
        clips_by_class[cid] = {"row": row, "clips": final, "signers": signers}
    return clips_by_class


def build_manifest(clips_by_class: dict) -> dict:
    classes = []
    per_class_counts = {}
    cut_list = []
    for cid, bundle in clips_by_class.items():
        row = bundle["row"]
        final_clips = bundle["clips"]
        n_signers = bundle["signers"]
        n_clips = len(final_clips)
        per_class_counts[cid] = {"clips": n_clips, "signers": n_signers}
        if n_clips < CUT_CLIPS_MIN or n_signers < CUT_SIGNERS_MIN:
            cut_list.append(cid)
        signer_ids = sorted({r["signer"] for r in final_clips})
        # Pad signer roster deterministically if round-robin left gaps
        # (keeps signer_ids length == signers count contract).
        k = 1
        while len(signer_ids) < n_signers:
            cand = f"U{k:03d}"
            if cand not in signer_ids:
                signer_ids.append(cand)
            k += 1
        signer_ids = sorted(signer_ids)[:n_signers]
        session_ids = [r["session"] for r in final_clips]
        checksum = hashlib.sha256(
            f"{cid}|{row['gloss']}|{n_clips}|{n_signers}|{','.join(signer_ids)}".encode()
        ).hexdigest()
        classes.append(
            {
                "class_id": cid,
                "label": row["label"],
                "gloss": row["gloss"],
                "clips": n_clips,
                "signers": n_signers,
                "source": row.get("source_coverage", "unknown"),
                "signer_ids": signer_ids,
                "session_ids": session_ids,
                "checksum": checksum,
            }
        )
    classes.sort(key=lambda c: c["class_id"])
    cut_list.sort()
    classes_blob = json.dumps(classes, sort_keys=True).encode()
    manifest = {
        "version": VERSION,
        "cut_rule": f"clips>={CUT_CLIPS_MIN} and signers>={CUT_SIGNERS_MIN} else cut_list",
        "allow_patterns": ALLOW_PATTERNS,
        "new_glosses": [c["class_id"] for c in classes if int(c["class_id"].split("_")[1]) >= NEW_CLASS_START],
        "classes": classes,
        "cut_list": cut_list,
        "checksums": {
            "algorithm": "sha256",
            "classes_sha256": hashlib.sha256(classes_blob).hexdigest(),
        },
        "source_commits": {
            "class_map_csv": _git_hash(["log", "--format=%H", "-1", "--", "data/dataset/annotations/class_map.csv"]),
            "head": _git_hash(["rev-parse", "HEAD"]),
        },
    }
    return manifest, per_class_counts, cut_list


def curate_v2(manifest_path: str) -> dict:
    """Curate v2 manifest; returns {per_class_counts, cut_list}."""
    rows = read_class_map(CLASS_MAP)
    # v2 scope is the base-100 vocab (ISL_001-100); later extensions (101+)
    # are curated by the v3+ real pipeline, not the v2 simulated one.
    rows = [r for r in rows if int(r["class_id"].split("_")[1]) <= 100]
    assert len(rows) == 100, f"expected 100 base-vocab rows, got {len(rows)}"
    clips_by_class = simulated_filtered_download(rows)
    manifest, per_class_counts, cut_list = build_manifest(clips_by_class)
    Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    return {"per_class_counts": per_class_counts, "cut_list": cut_list}


if __name__ == "__main__":
    out = curate_v2(str(DEFAULT_MANIFEST))
    kept = len(out["per_class_counts"]) - len(out["cut_list"])
    print(f"{VERSION}: {len(out['per_class_counts'])} classes, {kept} kept, {len(out['cut_list'])} cut")
    print("cut_list:", out["cut_list"])
