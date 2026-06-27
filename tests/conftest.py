"""Shared fixtures for generator script tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
FAKE_MODULES_DIR = FIXTURES_DIR / "modules"


@pytest.fixture
def fake_modules_dir(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point module discovery at tests/fixtures/modules for isolated edge-case tests."""
    import scripts.module_registry as registry

    monkeypatch.setattr(registry, "modules_dir", lambda: FAKE_MODULES_DIR)
    return FAKE_MODULES_DIR


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Empty generated-project directory with minimal scaffold files."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "requirements.txt").write_text("fastapi>=0.115.0\n")
    (root / ".env.example").write_text("LOG_LEVEL=INFO\n")
    (root / "docker-compose.yml").write_text(
        "services:\n  api:\n    build: .\n    ports:\n      - '8000:8000'\n"
    )
    (root / "Dockerfile").write_text(
        "FROM python:3.13-slim\nWORKDIR /app\n# MODULE: extra-copies\n"
    )
    target = root / "src" / "api" / "routes"
    target.mkdir(parents=True)
    (target / "__init__.py").write_text("router = None\n")
    return root
