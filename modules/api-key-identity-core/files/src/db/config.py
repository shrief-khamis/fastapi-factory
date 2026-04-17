from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class SeedUserSpec:
    """One seeded user: id, email, and plaintext API key (hashed before storage)."""

    user_id: str
    email: str
    api_key_plaintext: str


@dataclass(frozen=True)
class Settings:
    # SQLAlchemy async DB URL.
    # Examples:
    # - Postgres: postgresql+asyncpg://user:pass@host:5432/dbname
    # - SQLite (tests/dev): sqlite+aiosqlite:///./dev.db
    DATABASE_URL: str

    # Salt used to hash API keys before storing them in the DB.
    API_KEY_SALT: str

    # Parsed seed users (see _parse_seed_users).
    seed_users: tuple[SeedUserSpec, ...]

    # Legacy single-field accessors (first seed user, for backward compatibility).
    SEED_USER_ID: str
    SEED_USER_EMAIL: str
    SEED_API_KEY_PLAINTEXT: str | None


def _split_csv_list(raw: str) -> list[str]:
    return [p.strip() for p in raw.split(",") if p.strip()]


def _parse_seed_users() -> tuple[SeedUserSpec, ...]:
    """
    Multi-user: set all of SEED_USER_IDS, SEED_USER_EMAILS, SEED_API_KEY_PLAINTEXTS
    as comma-separated lists of equal length (order aligns: first with first, etc.).

    Single-user: set SEED_USER_ID, SEED_USER_EMAIL, SEED_API_KEY_PLAINTEXT (legacy).
    A single entry in the comma-separated lists is treated as one user.

    If no API key plaintext is configured, returns an empty tuple (nothing to seed).
    """
    ids_raw = os.getenv("SEED_USER_IDS")
    emails_raw = os.getenv("SEED_USER_EMAILS")
    keys_raw = os.getenv("SEED_API_KEY_PLAINTEXTS")

    if ids_raw is not None or emails_raw is not None or keys_raw is not None:
        if not (ids_raw and emails_raw and keys_raw):
            raise ValueError(
                "When using multi-user seeding, set all of SEED_USER_IDS, "
                "SEED_USER_EMAILS, and SEED_API_KEY_PLAINTEXTS (comma-separated, same length)."
            )
        ids = _split_csv_list(ids_raw)
        emails = _split_csv_list(emails_raw)
        keys = _split_csv_list(keys_raw)
        if len(ids) != len(emails) or len(ids) != len(keys):
            raise ValueError(
                f"SEED_USER_IDS ({len(ids)}), SEED_USER_EMAILS ({len(emails)}), "
                f"SEED_API_KEY_PLAINTEXTS ({len(keys)}) must have the same number of entries."
            )
        return tuple(SeedUserSpec(i, e, k) for i, e, k in zip(ids, emails, keys))

    key = os.getenv("SEED_API_KEY_PLAINTEXT") or None
    if not key:
        return ()
    return (
        SeedUserSpec(
            os.getenv("SEED_USER_ID", "00000000-0000-0000-0000-000000000001"),
            os.getenv("SEED_USER_EMAIL", "seed@example.com"),
            key,
        ),
    )


@lru_cache
def get_settings() -> Settings:
    seed_users = _parse_seed_users()
    first_id = (
        seed_users[0].user_id
        if seed_users
        else os.getenv("SEED_USER_ID", "00000000-0000-0000-0000-000000000001")
    )
    first_email = (
        seed_users[0].email
        if seed_users
        else os.getenv("SEED_USER_EMAIL", "seed@example.com")
    )
    first_key = seed_users[0].api_key_plaintext if seed_users else None
    return Settings(
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db"),
        API_KEY_SALT=os.getenv("API_KEY_SALT", "dev-api-key-salt"),
        seed_users=seed_users,
        SEED_USER_ID=first_id,
        SEED_USER_EMAIL=first_email,
        SEED_API_KEY_PLAINTEXT=first_key,
    )
