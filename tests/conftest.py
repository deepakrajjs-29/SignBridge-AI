"""Suite-wide test secret pin (Task 1): JWT_SECRET=test-secret, nothing else."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT / "backend", ROOT / "database" / "migrations", ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

os.environ["JWT_SECRET"] = "test-secret"

