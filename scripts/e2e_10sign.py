"""T6.2 — 10-sign staged E2E: frozen test clips -> REST predict -> DB chain -> WS reconnect."""
import csv, json, os, sys
from pathlib import Path
import numpy as np

os.environ.setdefault("JWT_SECRET", "test-secret")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from fastapi.testclient import TestClient
from app.main import app
from app.deps import reset_rate_limit

reset_rate_limit()
D = np.load(ROOT / "data/dataset/processed/tensors_mvp50.npz")
S = np.load(ROOT / "data/dataset/processed/split_idx.npz")
SC = np.load(ROOT / "models/scaler_mvp50.npz")
Xr, y = D["X"].astype("float32"), D["y"]
mu, sd = SC["mean"], SC["std"]
te = S["test"]
labels = {}
for r in csv.DictReader((ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8")):
    labels[r["class_id"]] = r["label"]
idx2cid = {}
for i, r in enumerate(sorted(labels)):
    idx2cid[i] = r

# fixed staged script: first test sample of classes 0..9 (deterministic, pre-registered)
picks = []
seen = set()
for i in te:
    if int(y[i]) < 10 and int(y[i]) not in seen:
        picks.append(int(i)); seen.add(int(y[i]))
picks.sort()
assert len(picks) == 10

client = TestClient(app, raise_server_exceptions=False)
sid = client.post("/api/v1/session", json={},
                  headers={"Authorization": "Bearer test-secret"}).json()["session_id"]

# NOTE: npz stores RAW wrist-normalized features; the API standardizes
# internally, so staged clips are sent verbatim (no inverse transform).
Watch = Xr[picks].tolist()
results = []
for k, frames in enumerate(Watch):
    r = client.post("/api/v1/predict", json={"frames": frames, "session_id": sid},
                    headers={"Authorization": "Bearer test-secret"})
    b = r.json()
    true_cid = idx2cid[int(y[picks[k]])]
    got = b.get("prediction", {}).get("class_id", "ERR")
    results.append({"true": true_cid, "true_label": labels[true_cid], "got": got,
                    "got_label": b.get("prediction", {}).get("label", ""),
                    "status": b.get("status", ""), "correct": got == true_cid,
                    "prediction_id": b.get("prediction", {}).get("prediction_id", "")})
correct = sum(r["correct"] for r in results)

# DB chain: sessions -> predictions rows exist for this session
sys.path.insert(0, str(ROOT / "backend"))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DBS
from app.models import Base, Prediction, RecognitionSession
eng = create_engine(f"sqlite:///{ROOT / 'signbridge_m1.db'}")
Base.metadata.create_all(eng)
with DBS(eng) as s:
    sess = s.get(RecognitionSession, sid)
    preds = s.query(Prediction).filter(Prediction.session_id == sid).all()
chain = {"session_row": sess is not None, "prediction_rows": len(preds)}

# WS reconnect: connect -> drop -> reconnect -> predict
with client.websocket_connect(f"/api/v1/stream?session_id={sid}") as ws:
    ws.receive_json(); ws.close()
reconnected = False
try:
    with client.websocket_connect(f"/api/v1/stream?session_id={sid}") as ws2:
        ws2.receive_json()
        ws2.send_json({"type": "start"})
        ws2.receive_json()
        for f in Watch[0][:45]:
            ws2.send_json({"type": "frame", "frame": f})
        p = ws2.receive_json()
        reconnected = p.get("type") == "prediction"
except Exception:
    reconnected = False

report = {"staged_10": results, "correct_10": correct,
          "db_chain": chain, "ws_reconnect_prediction": reconnected,
          "gate_90": correct >= 9}
(ROOT / "docs" / "M6_E2E.json").write_text(json.dumps(report, indent=1))
print(json.dumps({"correct_10": correct, "db_chain": chain,
                  "ws_reconnect": reconnected, "gate_90": correct >= 9}))
for r in results:
    print(f"  {r['true']} {r['true_label']:<12} -> {r['got']} {r['got_label']:<12} "
          f"{'OK' if r['correct'] else 'MISS'} ({r['status']})")
