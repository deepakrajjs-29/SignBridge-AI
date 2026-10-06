"""T4.5 — retention sweep (90/180/30/30) + log redaction helper."""
import os, sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import ApiLog, Base, Prediction, RecognitionSession

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
    out = {}
    with Session(eng) as s:
        for table, col, days in ((RecognitionSession, "sessions", POLICY["sessions_days"]),
                                 (Prediction, "predictions", POLICY["predictions_days"]),
                                 (ApiLog, "api_logs", POLICY["api_logs_days"])):
            cutoff = datetime.utcnow() - timedelta(days=days)
            n = s.query(table).filter(table.created_at < cutoff).delete()
            out[col] = n
        s.commit()
    return out


if __name__ == "__main__":
    print(sweep())
