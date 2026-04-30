"""Path setup so tests can import the api package as `ml_app_pkg`."""
from __future__ import annotations

import sys
from pathlib import Path

ML_APP_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ML_APP_DIR))

# Re-export the api package under a friendlier name for tests.
from api import main as ml_app_pkg  # noqa: E402,F401

sys.modules["ml_app_pkg"] = ml_app_pkg
