"""Task 3: real metrics + honest alerts (TDD: red first, then green)."""

import re

import numpy as np
from fastapi.testclient import TestClient

from app.deps import reset_rate_limit
from app.main import app

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-secret"}
FRAMES = (np.random.default_rng(0).normal(0, 0.5, (45, 189))).tolist()


def setup_function(_):
    reset_rate_limit()


def _sample(text: str, name: str) -> float:
    m = re.search(rf"^{re.escape(name)}\s+([0-9.eE+-]+)$", text, re.M)
    assert m, f"{name} not found in /metrics exposition"
    return float(m.group(1))


def test_metrics_endpoint_exposes_series():  # /metrics 200, contains http_requests_total
    r = client.get("/metrics")
    assert r.status_code == 200, r.text[:200]
    assert "http_requests_total" in r.text


def test_predict_observes_inference():  # POST /predict -> infer_seconds_count increments, model_loaded == 1
    before = _sample(client.get("/metrics").text, "infer_seconds_count")
    r = client.post("/api/v1/predict", json={"frames": FRAMES}, headers=AUTH)
    assert r.status_code == 200, r.text[:200]
    text = client.get("/metrics").text
    assert _sample(text, "infer_seconds_count") > before
    assert _sample(text, "model_loaded") == 1.0


def test_metrics_path_excluded_from_counts():  # controller: no scrape feedback loop on /metrics
    text = client.get("/metrics").text
    assert 'path="/metrics"' not in text
