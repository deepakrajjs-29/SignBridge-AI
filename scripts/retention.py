"""T4.5 — retention sweep (90/180/30/30) + log redaction helper."""
import os, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.models import ApiLog, Base, Feedback, Prediction, RecognitionSession

POLICY = {"sessions_days": 90, "predictions_days": 180, "api_logs_days": 30}
ROOT = Path(__file__).resolve().parents[1]


def redact(text: str) -> str:
    import re
    text = re.sub(r"(?i)(bearer\s+)\S+", r"\1***", text)
    return re.sub(r"(?i)(password|secret|token['\"]?\s*[:=]\s*)\S+", r"\1***", text)


def sweep(db_url: str | None = None) -> dict:
    url = db_url or os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'signbridge_m1.db'}")
    eng = create_engine(url)
    Base.metadata.create_all(eng)
    now = datetime.now(timezone.utc)  # tz-aware: naive cutoffs raise on PG timestamptz
    out = {}
    with Session(eng) as s:
        # Children first (PG FK order): feedback -> predictions -> sessions.
        pred_cutoff = now - timedelta(days=POLICY["predictions_days"])
        stale_preds = select(Prediction.prediction_id).where(
            Prediction.created_at < pred_cutoff)
        s.query(Feedback).filter(
            Feedback.prediction_id.in_(stale_preds)).delete(synchronize_session=False)
        out["predictions"] = s.query(Prediction).filter(
            Prediction.created_at < pred_cutoff).delete(synchronize_session=False)
        sess_cutoff = now - timedelta(days=POLICY["sessions_days"])
        out["sessions"] = s.query(RecognitionSession).filter(
            RecognitionSession.created_at < sess_cutoff,
            ~RecognitionSession.predictions.any()).delete(synchronize_session=False)
        logs_cutoff = now - timedelta(days=POLICY["api_logs_days"])
        out["api_logs"] = s.query(ApiLog).filter(
            ApiLog.created_at < logs_cutoff).delete(synchronize_session=False)
        s.commit()
    return out


if __name__ == "__main__":
    print(sweep())
