"""SQLite test database fixtures (schema from SQLAlchemy models, not Alembic)."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

# Test user + API key mirror the dev seed migration values.
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_USER_EMAIL = "seed@example.com"
TEST_API_KEY = "seed-api-key-plaintext"


def _clear_db_caches() -> None:
    from db.config import get_settings
    from db.session import get_engine, get_sessionmaker

    get_settings.cache_clear()
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


def _mock_redis_if_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """Celery templates ping Redis on startup; tests run without a broker."""
    try:
        import core.redis as redis_mod
    except ImportError:
        return
    monkeypatch.setattr(redis_mod, "ping_redis", lambda: True)


def _configure_database_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    monkeypatch.setenv("API_KEY_SALT", "dev-api-key-salt")
    _clear_db_caches()
    _mock_redis_if_present(monkeypatch)


async def create_test_schema() -> None:
    """Register all models on Base.metadata, then create tables."""
    import db.models  # noqa: F401 — includes usage/credit models when modules applied

    from db.init_db import create_schema

    await create_schema()


async def seed_identity(session) -> None:
    from db.auth import hash_api_key
    from db.config import get_settings
    from db.models import ApiKey, User

    settings = get_settings()
    session.add(User(id=TEST_USER_ID, email=TEST_USER_EMAIL))
    session.add(
        ApiKey(
            user_id=TEST_USER_ID,
            key_hash=hash_api_key(TEST_API_KEY, salt=settings.API_KEY_SALT),
            label="test",
        )
    )
    await session.commit()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-API-Key": TEST_API_KEY}


@pytest.fixture
async def client(monkeypatch: pytest.MonkeyPatch):
    """In-process HTTP client without DB setup (e.g. GET /health)."""
    _mock_redis_if_present(monkeypatch)
    from main import app as fastapi_app

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session(tmp_path, monkeypatch):
    """Async SQLAlchemy session backed by a fresh SQLite file per test."""
    _configure_database_env(monkeypatch, tmp_path)
    await create_test_schema()

    from db.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session


@pytest.fixture
async def seeded_db(db_session):
    """DB session with one user and a valid API key."""
    await seed_identity(db_session)
    return db_session


@pytest.fixture
async def app(tmp_path, monkeypatch):
    """FastAPI app with SQLite schema created from ORM models."""
    _configure_database_env(monkeypatch, tmp_path)
    await create_test_schema()
    await _seed_identity_standalone()

    from main import app as fastapi_app

    return fastapi_app


async def _seed_identity_standalone() -> None:
    from db.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        await seed_identity(session)


@pytest.fixture
async def db_client(app):
    """In-process HTTP client with SQLite DB and seeded identity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
