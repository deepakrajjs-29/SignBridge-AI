"""T8.2 — prod smoke suite (health/model/classes/predict/tts/t2s/history/admin/ws)."""
import os, sys
os.environ.setdefault("JWT_SECRET", "test-secret")
sys.path.insert(0, "D:/Projects/SignBridge/backend")
from pathlib import Path
import numpy as np
from fastapi.testclient import TestClient
from app.main import app
from app.deps import reset_rate_limit

reset_rate_limit()
H = {"Authorization": "Bearer test-secret"}
c = TestClient(app, raise_server_exceptions=False)
checks = []

def check(name, cond, detail=""):
    checks.append({"check": name, "pass": bool(cond), "detail": detail})

r = c.get("/health"); check("health 200", r.status_code == 200)
m = c.get("/api/v1/model").json()
check("model version pinned", m["model"]["model_version"] == "SBAI-MDL-ISL-1.0.0", m["model"]["model_version"])
check("classes == 50", c.get("/api/v1/classes").json()["count"] == 50)
fr = (np.random.default_rng(9).normal(0, 0.5, (45, 189))).tolist()
p = c.post("/api/v1/predict", json={"frames": fr}, headers=H).json()
check("predict 200 + timing", p.get("success") and p.get("processing_time_ms", 9999) < 200000,
      f"{p.get('prediction',{}).get('class_id')} {p.get('processing_time_ms')}ms")
t = c.post("/api/v1/tts", json={"text": "Hello"}, headers=H)
check("tts contract (501 flagged)", t.status_code == 501 and "TTS_NOT_CONFIGURED" in t.text)
s = c.post("/api/v1/text-to-sign", json={"text": "Hello xyzzy"}, headers=H).json()
check("text-to-sign + unsupported flag", s["items"] and s["unsupported_words"] == ["xyzzy"])
sid = c.post("/api/v1/session", json={}, headers=H).json()["session_id"]
c.post("/api/v1/predict", json={"frames": fr, "session_id": sid}, headers=H)
h = c.get(f"/api/v1/sessions/{sid}/predictions", headers=H).json()
check("history write/read", len(h["predictions"]) >= 1)
a = c.get("/api/v1/admin/models", headers=H)
check("admin health", a.status_code == 200 and bool(a.json()["models"]))
with c.websocket_connect(f"/api/v1/stream?session_id={sid}") as ws:
    ws.receive_json(); ws.send_json({"type": "start"}); ws.receive_json()
    for f in fr:
        ws.send_json({"type": "frame", "frame": f})
    check("ws prediction", ws.receive_json().get("type") == "prediction")

fails = [x for x in checks if not x["pass"]]
print(f"smoke: {len(checks)-len(fails)}/{len(checks)} PASS")
for x in checks:
    print(f"  [{'OK' if x['pass'] else 'FAIL'}] {x['check']} {x['detail']}")
sys.exit(1 if fails else 0)
