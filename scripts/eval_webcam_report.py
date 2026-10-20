"""Webcam manual-protocol report — accuracy / coverage / flips from a truth CSV.

Usage:
  py -3 scripts/eval_webcam_report.py --truth truth.csv --out report.json

Truth CSV columns (pinned by the plan):
  attempt_id,expected_class_id,displayed_label,displayed_state,displayed_conf,flips_in_attempt,notes
The template (Docs/eval/webcam_truth_template.csv) stores those names as plain
CSV (no spaces after commas); this parser accepts both forms (skipinitialspace
+ stripped header names) so hand-edited files still load.

Correctness / label<->id mapping rule: the truth CSV records the label the app
DISPLAYED (no displayed class_id column), so a valid row is judged via
  correct = class_map[expected_class_id] == displayed_label
looked up in data/dataset/annotations/class_map.csv (``class_id,label``,
override with --class-map), compared case-insensitively and whitespace-trimmed.
If expected_class_id is unknown to the class map, or displayed_label is empty,
the label<->id lookup FAILED: the row is excluded from every metric and counted
in ``n_mapping_failed``.

Row validity: rows whose ``notes`` field is ``invalid`` (case-insensitive) are
excluded from all metrics and counted in ``n_notes_invalid``; mapping failures
are counted in ``n_mapping_failed`` and folded into ``n_invalid`` so that
  n_invalid = n_notes_invalid + n_mapping_failed and n_valid = n - n_invalid
(each report carries an internal assert that this holds).

displayed_state is compared case-insensitively (``Recognized`` from the WS path
vs ``recognized`` from REST): a row counts as recognized only for exactly
``recognized``.

Metric definitions — flip_rate was left open by the plan, so BOTH definitions
are reported:
  overall_accuracy        = #(correct AND recognized) / n_valid
  accepted_accuracy       = #(correct AND recognized) / #recognized
                            (0.0 when no row is recognized)
  coverage                = #recognized / n_valid
  flip_rate               = mean(flips_in_attempt) over the n_valid rows
                            (0.0 when n_valid == 0)  [mean-flips definition]
  attempts_with_flip_rate = #(flips_in_attempt >= 1) / n_valid (0.0 if none)
                            [fraction-of-attempts-with-a-flip definition]
  per_class[expected_class_id] = {n, recognized, correct_recognized,
                                  accepted_accuracy}
(n_valid == 0 — every row excluded/invalid, but the header was valid — yields
all-zero metrics and an empty per_class table; that is NOT an error.)

Malformed / empty truth CSV -> ``ValueError`` from ``run()`` (or exit code 2
from ``main()``, which prints ``ERROR: ...`` to stderr): empty file / no header,
missing required header columns, a row with too few/many fields, a non-integer
or negative flips_in_attempt, a non-numeric displayed_conf (blank is allowed
and means "no confidence shown" — displayed_conf feeds no metric), an
unreadable path, or a header with zero data rows (template not filled in).

Standard library only (NumPy permitted by the task, not needed here).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRUTH_COLUMNS = ["attempt_id", "expected_class_id", "displayed_label",
                 "displayed_state", "displayed_conf", "flips_in_attempt", "notes"]
CLASS_MAP_PATH = ROOT / "data/dataset" / "annotations" / "class_map.csv"
RECOGNIZED = "recognized"


def load_class_map(path: str | Path | None = None) -> dict[str, str]:
    """class_id -> label from class_map.csv (``class_id,label`` headers)."""
    p = Path(path) if path else CLASS_MAP_PATH
    with p.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, skipinitialspace=True)
        if not reader.fieldnames:
            raise ValueError(f"{p}: empty class map (no header row)")
        fields = [(f or "").strip() for f in reader.fieldnames]
        if "class_id" not in fields or "label" not in fields:
            raise ValueError(f"{p}: class map needs 'class_id,label' headers, got {fields}")
        out: dict[str, str] = {}
        for raw in reader:
            row = {(k or "").strip(): (v or "").strip()
                   for k, v in raw.items() if k is not None}
            if row.get("class_id"):
                out[row["class_id"]] = row.get("label", "")
    if not out:
        raise ValueError(f"{p}: class map has no data rows")
    return out


def _read_rows(path: str | Path) -> list[dict]:
    """Parse + structurally validate the truth CSV (raises ValueError)."""
    p = Path(path)
    try:
        fh = p.open(encoding="utf-8", newline="")
    except OSError as e:
        raise ValueError(f"cannot read truth CSV {p}: {e}") from e
    with fh:
        reader = csv.DictReader(fh, skipinitialspace=True)
        if not reader.fieldnames:
            raise ValueError(f"{p}: malformed/empty truth CSV (no header row)")
        fields = [(f or "").strip() for f in reader.fieldnames]
        missing = [c for c in TRUTH_COLUMNS if c not in fields]
        if missing:
            raise ValueError(
                f"{p}: malformed truth CSV — missing header column(s): "
                f"{', '.join(missing)}; expected {','.join(TRUTH_COLUMNS)}")
        rows: list[dict] = []
        for lineno, raw in enumerate(reader, start=2):
            if None in raw:
                raise ValueError(f"{p}:{lineno}: malformed truth CSV — too many fields")
            if any(v is None for v in raw.values()):
                raise ValueError(f"{p}:{lineno}: malformed truth CSV — too few fields")
            row = {(k or "").strip(): (v or "").strip() for k, v in raw.items()}
            conf = row["displayed_conf"]
            if conf:
                try:
                    float(conf)
                except ValueError as e:
                    raise ValueError(
                        f"{p}:{lineno}: malformed displayed_conf {conf!r} (number or blank)"
                    ) from e
            flips = row["flips_in_attempt"]
            try:
                flips_i = int(flips)
            except ValueError as e:
                raise ValueError(
                    f"{p}:{lineno}: malformed flips_in_attempt {flips!r} (non-negative integer)"
                ) from e
            if flips_i < 0:
                raise ValueError(f"{p}:{lineno}: malformed flips_in_attempt {flips_i} (negative)")
            rows.append({
                "attempt_id": row["attempt_id"],
                "expected_class_id": row["expected_class_id"],
                "displayed_label": row["displayed_label"],
                "displayed_state": row["displayed_state"],
                "flips_in_attempt": flips_i,
                "notes": row["notes"],
            })
    if not rows:
        raise ValueError(f"{p}: truth CSV has a header but no data rows")
    return rows


def compute_report(rows: list[dict], class_map: dict[str, str]) -> dict:
    """Metric dict over already-parsed truth rows (see module docstring)."""
    n = len(rows)
    n_notes_invalid = sum(1 for r in rows if r["notes"].casefold() == "invalid")

    valid: list[dict] = []
    n_mapping_failed = 0
    for r in rows:
        if r["notes"].casefold() == "invalid":
            continue
        expected_label = class_map.get(r["expected_class_id"].strip())
        displayed = r["displayed_label"].strip()
        if expected_label is None or not displayed:
            n_mapping_failed += 1
            continue
        valid.append({
            **r,
            "_recognized": r["displayed_state"].strip().casefold() == RECOGNIZED,
            "_correct": displayed.casefold() == expected_label.strip().casefold(),
        })

    n_valid = len(valid)
    n_invalid = n_notes_invalid + n_mapping_failed
    assert n_valid + n_invalid == n, "valid + invalid must sum to n"
    n_recognized = sum(1 for r in valid if r["_recognized"])
    n_correct_rec = sum(1 for r in valid if r["_recognized"] and r["_correct"])
    flips = [r["flips_in_attempt"] for r in valid]

    def _rate(num: int, den: int) -> float:
        return round(num / den, 6) if den else 0.0

    per_class: dict[str, dict] = {}
    for cid in sorted({r["expected_class_id"].strip() for r in valid}):
        rs = [r for r in valid if r["expected_class_id"].strip() == cid]
        rec = sum(1 for r in rs if r["_recognized"])
        ok = sum(1 for r in rs if r["_recognized"] and r["_correct"])
        per_class[cid] = {"n": len(rs), "recognized": rec, "correct_recognized": ok,
                          "accepted_accuracy": _rate(ok, rec)}

    return {
        "n": n,
        "n_valid": n_valid,
        "n_invalid": n_invalid,
        "n_notes_invalid": n_notes_invalid,
        "n_mapping_failed": n_mapping_failed,
        "n_recognized": n_recognized,
        "n_correct_recognized": n_correct_rec,
        "overall_accuracy": _rate(n_correct_rec, n_valid),
        "accepted_accuracy": _rate(n_correct_rec, n_recognized),
        "coverage": _rate(n_recognized, n_valid),
        "flip_rate": round(sum(flips) / n_valid, 6) if n_valid else 0.0,
        "attempts_with_flip_rate": _rate(sum(1 for f in flips if f >= 1), n_valid),
        "per_class": per_class,
    }


def run(truth: str | Path, class_map_path: str | Path | None = None) -> dict:
    """Read the truth CSV + class map and return the report dict (ValueError on malformed input)."""
    class_map = load_class_map(class_map_path)
    return compute_report(_read_rows(truth), class_map)


def main(argv: list[str] | None = None) -> int:
    P = argparse.ArgumentParser(description=__doc__)
    P.add_argument("--truth", required=True, help="truth CSV (see Docs/eval/webcam_truth_template.csv)")
    P.add_argument("--out", required=True, help="report JSON output path")
    P.add_argument("--class-map", default=None,
                   help=f"class_id,label CSV (default {CLASS_MAP_PATH})")
    A = P.parse_args(argv)
    try:
        report = run(A.truth, A.class_map)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr, flush=True)
        return 2
    out_path = Path(A.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out_path}", flush=True)
    print(json.dumps(report, indent=1), flush=True)
    print("WEBCAM REPORT OK", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
