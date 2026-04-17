from __future__ import annotations

from sqlalchemy import select

from db.auth import hash_api_key
from db.config import get_settings
from db.models import ApiKey, User
from db.session import get_sessionmaker


async def seed_from_env() -> None:
    """
    Seed users and API keys from environment variables.

    Supports:
    - Multi-user: SEED_USER_IDS, SEED_USER_EMAILS, SEED_API_KEY_PLAINTEXTS      (comma-separated lists, same length; one user per index).
    - Single-user (legacy): SEED_USER_ID, SEED_USER_EMAIL, SEED_API_KEY_PLAINTEXT.

    Idempotent: skips creating a user that already exists by id, and skips
    an API key row if that key_hash already exists.
    """

    settings = get_settings()
    if not settings.seed_users:
        return

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        for spec in settings.seed_users:
            key_hash = hash_api_key(
                spec.api_key_plaintext, salt=settings.API_KEY_SALT
            )

            user_stmt = select(User).where(User.id == spec.user_id)
            user_result = await session.execute(user_stmt)
            user = user_result.scalars().first()
            if user is None:
                user = User(id=spec.user_id, email=spec.email)
                session.add(user)
            else:
                # Keep email in sync if you changed env (optional hygiene).
                if user.email != spec.email:
                    user.email = spec.email

            key_stmt = select(ApiKey).where(ApiKey.key_hash == key_hash)
            key_result = await session.execute(key_stmt)
            api_key = key_result.scalars().first()
            if api_key is None:
                session.add(
                    ApiKey(
                        user_id=user.id,
                        key_hash=key_hash,
                        label="seed",
                    )
                )

        await session.commit()
