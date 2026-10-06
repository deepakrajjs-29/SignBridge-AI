"""Suite-wide test secret pin (Task 1): JWT_SECRET=test-secret, nothing else."""

import os

os.environ["JWT_SECRET"] = "test-secret"
