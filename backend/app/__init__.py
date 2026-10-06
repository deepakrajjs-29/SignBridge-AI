"""SignBridge AI backend package.

Auto-loads operator `.env` files at `import app` time, before any `app.*`
submodule reads `os.getenv`: `<repo>/backend/.env` first, then `<repo>/.env`.
Explicit process environment always wins (`override=False`).
"""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

_log = logging.getLogger(__name__)


def _load_operator_env() -> list[str]:
    loaded: list[str] = []
    backend_env = Path(__file__).resolve().parents[1] / ".env"
    repo_env = Path(__file__).resolve().parents[2] / ".env"
    for candidate in (backend_env, repo_env):
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            loaded.append(str(candidate))
    return loaded


_loaded_from = _load_operator_env()
_log.info("app env loaded from: %s", _loaded_from or "no .env file found")
