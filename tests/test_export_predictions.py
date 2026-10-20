"""Task 9 Step 1 — scripts/export_predictions.py round-trip (REST persist -> CSV).

Modelled on tests/test_history.py: TestClient + Bearer test-secret, rate limit
reset per test. REST POST /api/v1/predict persists a Prediction row for the
given session_id *unconditionally* for any non-no-sign outcome — even a
provisional/uncertain confidence still writes history (WS does not), so the
export must show the row whatever ``status`` came back.
"""

import csv
import importlib.util
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

from app.deps import reset_rate_limit
from app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-secret"}
FRAMES = (np.random.default_rng(1).normal(0, 0.5, (45, 189))).tolist()
ROOT = Path(__file__).resolve().parents[1]
HEADER = ["prediction_id", "session_id", "class_id", "confidence", "model_id", "created_at"]


def setup_function(_):
    reset_rate_limit()


def _load_export_module():
    """Load scripts/export_predictions.py as a plain module (no package import)."""
    path = ROOT / "scripts" / "export_predictions.py"
    spec = importlib.util.spec_from_file_location("export_predictions", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_export_predictions_writes_session_rows(tmp_path):
    """REST-persisted prediction (any status) is exported with matching values."""
    sid = client.post("/api/v1/session", json={}, headers=AUTH).json()["session_id"]
    r = client.post("/api/v1/predict", json={"frames": FRAMES, "session_id": sid}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    pred = r.json()["prediction"]
    assert pred.get("prediction_id"), "REST must persist even a provisional/uncertain answer"
    # status may be recognized/provisional/uncertain — persistence is unconditional
    out = tmp_path / "preds.csv"
    n = _load_export_module().run(session_id=sid, out=out)
    assert out.exists()
    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == HEADER
    assert n >= 1 and len(rows) - 1 == n, (n, len(rows))
    match = [row for row in rows[1:] if row[0] == pred["prediction_id"]]
    assert match, f"session {sid} row missing from CSV: {rows}"
    row = match[0]
    assert row[1] == sid
    assert row[2] == pred["class_id"], (row, pred)
    assert float(row[3]) == float(pred["confidence"]), (row, pred)
    assert row[4]  # model_id persisted
    assert row[5]  # created_at persisted (ISO timestamp)


def test_export_predictions_unknown_session_header_only(tmp_path):
    """Unknown session -> CSV with the header row only, 0 rows, no error."""
    out = tmp_path / "unknown.csv"
    n = _load_export_module().run(session_id="sess_does_not_exist_000", out=out)
    assert n == 0
    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    assert rows == [HEADER]


def test_export_predictions_cli_main(tmp_path):
    """main(argv) — the documented CLI shape — exits 0 and writes the CSV."""
    mod = _load_export_module()
    sid = client.post("/api/v1/session", json={}, headers=AUTH).json()["session_id"]
    r = client.post("/api/v1/predict", json={"frames": FRAMES, "session_id": sid}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    out = tmp_path / "cli_preds.csv"
    rc = mod.main(["--session", sid, "--out", str(out)])
    assert rc == 0
    with out.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == HEADER
    assert any(row[1] == sid for row in rows[1:]), rows
    # unknown session via the CLI also exits 0 (documented header-only behavior)
    rc2 = mod.main(["--session", "sess_nope_000", "--out", str(tmp_path / "empty.csv")])
    assert rc2 == 0
