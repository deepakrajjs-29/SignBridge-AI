"""Export persisted Prediction rows for one session to CSV (M13 Task 9).

Usage:
  py -3 scripts/export_predictions.py --session <sid> --out preds.csv

Reads ``app.models.Prediction`` rows for ``--session`` through the repo's own
DB access pattern — ``app.deps.get_db_session()`` (DATABASE_URL honored at call
time, SQLite default ``<repo>/signbridge_m1.db``, tables create_all'd once per
engine) — and writes one CSV row per prediction:

  prediction_id,session_id,class_id,confidence,model_id,created_at

Header = the five fields pinned by the plan (session_id, class_id, confidence,
model_id, created_at — as defined in backend/app/models.py) plus the table's
primary key ``prediction_id``. ``status`` and ``sequence_id`` are intentionally
NOT exported (the plan pins the column set above).

Unknown session (or any session with zero rows): the CSV is still written with
the header row only and a one-line message is printed; the exit code stays 0.

``run()`` returns the number of data rows written and ``main(argv)`` returns
the exit code, so the script is both importable/testable and runnable as shown.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.deps import get_db_session  # noqa: E402
from app.models import Prediction  # noqa: E402

HEADER = ["prediction_id", "session_id", "class_id", "confidence", "model_id", "created_at"]


def _cell(value) -> str:
    """CSV-render one column: None -> empty, datetimes -> ISO, else str()."""
    if value is None:
        return ""
    isoformat = getattr(value, "isoformat", None)
    if callable(isoformat):
        return isoformat()
    return str(value)


def run(session_id: str, out: str | Path) -> int:
    """Write all Prediction rows for ``session_id`` to ``out`` (CSV).

    Returns the number of data rows written (0 for an unknown session — the
    file still gets its header row). Rows are ordered by created_at, then
    prediction_id for a stable tie-break.
    """
    with get_db_session() as db:
        rows = (db.query(Prediction)
                .filter(Prediction.session_id == session_id)
                .order_by(Prediction.created_at, Prediction.prediction_id)
                .all())
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(HEADER)
        for r in rows:
            writer.writerow([_cell(r.prediction_id), _cell(r.session_id), _cell(r.class_id),
                             _cell(r.confidence), _cell(r.model_id), _cell(r.created_at)])
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    P = argparse.ArgumentParser(description=__doc__)
    P.add_argument("--session", required=True, help="session_id to export")
    P.add_argument("--out", required=True, help="CSV output path")
    A = P.parse_args(argv)
    n = run(A.session, A.out)
    if n:
        print(f"wrote {n} prediction row(s) -> {A.out}", flush=True)
    else:
        print(f"no predictions for session {A.session!r}: wrote header-only CSV -> {A.out}",
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
