"""Prometheus instrumentation (Task 3): real request/inference/model-load series.

Series produced:
- http_requests_total{path,code} — every HTTP response except GET /metrics itself
  (excluded to avoid scrape feedback loops).
- http_5xx_total — count of HTTP responses with 5xx status.
- infer_seconds — histogram of model inference latency, observed in BOTH the
  REST predict path (app/routers/predict.py::infer) and the WebSocket stream
  path (app/routers/stream.py::stream).
- model_loaded — gauge, 0 until the first successful model load, then 1
  (set in app/deps.py::get_model post-load).
"""

from __future__ import annotations

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "HTTP responses by path and status code.",
    ["path", "code"],
)

HTTP_5XX_TOTAL = Counter(
    "http_5xx_total",
    "HTTP responses with 5xx status.",
)

INFER_SECONDS = Histogram(
    "infer_seconds",
    "Model inference latency in seconds (predict + stream paths).",
)

MODEL_LOADED = Gauge(
    "model_loaded",
    "1 once the recognition model has loaded successfully, else 0.",
)
MODEL_LOADED.set(0)


def exposition() -> tuple[bytes, str]:
    """Return (body, content_type) for the GET /metrics endpoint."""
    return generate_latest(), CONTENT_TYPE_LATEST
