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


@lru_cache
def get_settings() -> Settings:
    return Settings(
        DATABASE_URL=os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/myapi"
        ),
        API_KEY_SALT=os.getenv("API_KEY_SALT", "dev-api-key-salt"),
    )
