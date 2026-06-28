"""Pytest entrypoint when api_key_identity_core is applied (replaces template conftest)."""

import sys
from pathlib import Path

# Allow pytest_plugins to resolve conftest_db next to this file.
_tests_dir = Path(__file__).resolve().parent
if str(_tests_dir) not in sys.path:
    sys.path.insert(0, str(_tests_dir))

pytest_plugins = ["conftest_db"]
