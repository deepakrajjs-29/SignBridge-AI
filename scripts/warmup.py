"""Task 2 — container warmup probe (stdlib only, no new dependencies).

Polls GET /health up to --timeout seconds, then fires one warmup
POST /predict with a deterministic SEQ_LEN x FEAT_DIM zero payload.
Exit code 0 = warmup predict accepted; non-zero = failed/missing server.

Self-check: ``py scripts/warmup.py --help`` exits 0.
Unit probe: import :func:`build_warmup_payload` and assert its shape.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

SEQ_LEN = 45
FEAT_DIM = 189


def build_warmup_payload(seq_len: int = SEQ_LEN, feat_dim: int = FEAT_DIM) -> list[list[float]]:
    """Deterministic zero payload matching the training window shape."""
    return [[0.0] * feat_dim for _ in range(seq_len)]


def _get(base_url: str, path: str, timeout: float) -> tuple[int, str]:
    req = urllib.request.Request(base_url.rstrip("/") + path, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def _post_json(base_url: str, path: str, payload: dict, token: str, timeout: float) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(base_url.rstrip("/") + path, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def wait_for_health(base_url: str, timeout: float = 60.0, interval: float = 2.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            status, _ = _get(base_url, "/health", timeout=5)
            if status == 200:
                return True
        except OSError:
            pass
        time.sleep(interval)
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Warm the SignBridge backend (poll /health, one warmup /predict).")
    ap.add_argument("--base-url", default=os.getenv("WARMUP_BASE_URL", "http://localhost:8000"))
    ap.add_argument("--wait", action="store_true", default=True,
                    help="Poll /health before the warmup predict (default: on).")
    ap.add_argument("--no-wait", dest="wait", action="store_false", help="Skip the health poll.")
    ap.add_argument("--timeout", type=float, default=60.0, help="Health-poll budget in seconds.")
    ap.add_argument("--token", default=os.getenv("JWT_SECRET", ""),
                    help="Bearer token for /predict (default: $JWT_SECRET).")
    ap.add_argument("--seq-len", type=int, default=SEQ_LEN)
    ap.add_argument("--feat-dim", type=int, default=FEAT_DIM)
    args = ap.parse_args(argv)

    if args.wait and not wait_for_health(args.base_url, timeout=args.timeout):
        print(f"warmup: /health not ready within {args.timeout:g}s at {args.base_url}", file=sys.stderr)
        return 1

    payload = {"frames": build_warmup_payload(args.seq_len, args.feat_dim)}
    try:
        status, body = _post_json(args.base_url, "/api/v1/predict", payload, args.token, timeout=120)
    except OSError as e:
        print(f"warmup: predict request failed: {e}", file=sys.stderr)
        return 1
    if status != 200:
        print(f"warmup: predict returned {status}: {body[:300]}", file=sys.stderr)
        return 1
    try:
        doc = json.loads(body)
    except json.JSONDecodeError:
        print(f"warmup: non-JSON predict reply: {body[:300]}", file=sys.stderr)
        return 1
    if not doc.get("success"):
        print(f"warmup: predict success=false: {body[:300]}", file=sys.stderr)
        return 1
    print(f"warmup: ok via {args.base_url} "
          f"(class={doc.get('prediction', {}).get('class_id')} "
          f"ms={doc.get('processing_time_ms')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
