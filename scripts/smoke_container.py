"""Task 2 — HTTP container smoke over real HTTP (stdlib only, no new dependencies).

Asserts health/model/classes/predict/text-to-sign against a live backend::

    py scripts/smoke_container.py --base-url http://localhost:8000

Exit code 0 = all checks pass; 1 = any failure. ``--token`` defaults to
``$JWT_SECRET`` (predict/text-to-sign require Bearer auth).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

SEQ_LEN = 45
FEAT_DIM = 189


def build_payload(seq_len: int = SEQ_LEN, feat_dim: int = FEAT_DIM) -> list[list[float]]:
    return [[0.0] * feat_dim for _ in range(seq_len)]


class Client:
    def __init__(self, base_url: str, token: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _req(self, method: str, path: str, payload: dict | None = None) -> tuple[int, dict | str]:
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            try:
                return e.code, json.loads(raw)
            except json.JSONDecodeError:
                return e.code, raw
        try:
            return 200, json.loads(raw)
        except json.JSONDecodeError:
            return 200, raw


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="HTTP smoke for the composed SignBridge backend.")
    ap.add_argument("--base-url", default=os.getenv("SMOKE_BASE_URL", "http://localhost:8000"))
    ap.add_argument("--token", default=os.getenv("JWT_SECRET", ""),
                    help="Bearer token (default: $JWT_SECRET).")
    args = ap.parse_args(argv)

    c = Client(args.base_url, args.token)
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        checks.append((name, bool(cond), detail))
        print(f"  [{'OK' if cond else 'FAIL'}] {name} {detail}".rstrip())

    status, body = c._req("GET", "/health")
    check("health 200 + status ok", status == 200 and isinstance(body, dict)
          and body.get("status") == "ok", f"http={status}")

    status, body = c._req("GET", "/api/v1/model")
    ok = (status == 200 and isinstance(body, dict) and isinstance(body.get("model"), dict)
          and body["model"].get("model_version") == "SBAI-MDL-ISL-1.0.0"
          and body["model"].get("seq_len") == SEQ_LEN
          and body["model"].get("feat_dim") == FEAT_DIM)
    check("model version/shape pinned", ok, f"http={status}")

    status, body = c._req("GET", "/api/v1/classes")
    ok = status == 200 and isinstance(body, dict) and body.get("count", 0) > 0
    check("classes non-empty", ok, f"http={status} count={(body.get('count') if isinstance(body, dict) else '?')}")

    status, body = c._req("POST", "/api/v1/predict", {"frames": build_payload()})
    ok = (status == 200 and isinstance(body, dict) and body.get("success") is True
          and isinstance(body.get("prediction"), dict))
    detail = (f"http={status} class={body.get('prediction', {}).get('class_id')}"
              if isinstance(body, dict) else f"http={status}")
    check("predict 200 + prediction", ok, detail)

    status, body = c._req("POST", "/api/v1/text-to-sign", {"text": "hello"})
    ok = status == 200 and isinstance(body, dict) and body.get("success") is True and "items" in body
    check("text-to-sign 200 + items", ok, f"http={status}")

    fails = [n for n, p, _ in checks if not p]
    print(f"smoke_container: {len(checks) - len(fails)}/{len(checks)} PASS vs {args.base_url}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
