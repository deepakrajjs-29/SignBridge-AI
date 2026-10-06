"""Task 5 — retention sweep: children-first deletes with tz-aware cutoffs (PG-correct).

Own tmp sqlite via ``tmp_path``; never touches the dev DB.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import ApiLog, Base, Feedback, ModelVersion, Prediction, RecognitionSession, SignClass


def _load_sweep():
    """Load sweep() from scripts/retention.py (plain script, no package)."""
    import importlib.util

    path = ROOT / "scripts" / "retention.py"
    spec = importlib.util.spec_from_file_location("retention", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.sweep


def _naive_utc_ago(days: float) -> datetime:
    """Naive-UTC timestamp ``days`` in the past (sqlite round-trips exactly)."""
    return datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)


def _seed_parents(s: Session) -> None:
    s.merge(SignClass(class_id="CLS_T5", label="T5"))
    s.merge(ModelVersion(model_id="mdl-t5", version="v-t5", model_type="lstm",
                         seq_len=45, feat_dim=189, status="active"))
    s.commit()


def test_sweep_deletes_children_first(tmp_path):
    sweep = _load_sweep()
    db = tmp_path / "ret_old.db"
    eng = create_engine(f"sqlite:///{db}")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        _seed_parents(s)
        s.add(RecognitionSession(session_id="sess-old", created_at=_naive_utc_ago(100)))
        s.add(Prediction(prediction_id="pred-old", session_id="sess-old", class_id="CLS_T5",
                         model_id="mdl-t5", confidence=0.9, created_at=_naive_utc_ago(200)))
        s.add(Feedback(feedback_id="fb-old", prediction_id="pred-old",
                       created_at=_naive_utc_ago(200)))
        s.add(ApiLog(request_id="log-old", path="/p", status_code=200,
                     created_at=_naive_utc_ago(40)))
        s.commit()

    out = sweep(f"sqlite:///{db}")

    assert out == {"sessions": 1, "predictions": 1, "api_logs": 1}
    with Session(eng) as s:
        assert s.query(RecognitionSession).count() == 0
        assert s.query(Prediction).count() == 0
        assert s.query(Feedback).count() == 0  # no orphan feedback left behind
        assert s.query(ApiLog).count() == 0


def test_sweep_keeps_fresh_rows(tmp_path):
    sweep = _load_sweep()
    db = tmp_path / "ret_fresh.db"
    eng = create_engine(f"sqlite:///{db}")
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        _seed_parents(s)
        now = _naive_utc_ago(0)
        s.add(RecognitionSession(session_id="sess-new", created_at=now))
        s.add(Prediction(prediction_id="pred-new", session_id="sess-new", class_id="CLS_T5",
                         model_id="mdl-t5", confidence=0.9, created_at=now))
        s.add(Feedback(feedback_id="fb-new", prediction_id="pred-new", created_at=now))
        s.add(ApiLog(request_id="log-new", path="/p", status_code=200, created_at=now))
        s.commit()

    out = sweep(f"sqlite:///{db}")

    assert out == {"sessions": 0, "predictions": 0, "api_logs": 0}
    with Session(eng) as s:
        assert s.query(RecognitionSession).count() == 1
        assert s.query(Prediction).count() == 1
        assert s.query(Feedback).count() == 1
        assert s.query(ApiLog).count() == 1
