from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    # SQLAlchemy async DB URL.
    # Examples:
    # - Postgres: postgresql+asyncpg://user:pass@host:5432/dbname
    # - SQLite (tests/dev): sqlite+aiosqlite:///./dev.db
    DATABASE_URL: str

    # Salt used to hash API keys before storing them in the DB.
    API_KEY_SALT: str

    # Seed defaults (used by scripts/seed_db.py).
    SEED_USER_ID: str
    SEED_USER_EMAIL: str
    SEED_API_KEY_PLAINTEXT: str | None


@lru_cache
def get_settings() -> Settings:
    return Settings(
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db"),
        API_KEY_SALT=os.getenv("API_KEY_SALT", "dev-api-key-salt"),
        SEED_USER_ID=os.getenv(
            "SEED_USER_ID", "00000000-0000-0000-0000-000000000001"
        ),
        SEED_USER_EMAIL=os.getenv("SEED_USER_EMAIL", "seed@example.com"),
        SEED_API_KEY_PLAINTEXT=os.getenv("SEED_API_KEY_PLAINTEXT") or None,
    )

