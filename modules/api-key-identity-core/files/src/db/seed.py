from __future__ import annotations

from sqlalchemy import select

from db.auth import hash_api_key
from db.config import get_settings
from db.models import ApiKey, User
from db.session import get_sessionmaker


async def seed_from_env() -> None:
    """
    Seed an initial user + API key based on environment variables.

    Designed to be idempotent: if the key already exists, it does nothing.
    """

    settings = get_settings()
    if not settings.SEED_API_KEY_PLAINTEXT:
        return

    key_hash = hash_api_key(settings.SEED_API_KEY_PLAINTEXT, salt=settings.API_KEY_SALT)

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        # Ensure user exists.
        user_stmt = select(User).where(User.id == settings.SEED_USER_ID)
        user_result = await session.execute(user_stmt)
        user = user_result.scalars().first()
        if user is None:
            user = User(id=settings.SEED_USER_ID, email=settings.SEED_USER_EMAIL)
            session.add(user)

        # Ensure API key exists.
        key_stmt = select(ApiKey).where(ApiKey.key_hash == key_hash)
        key_result = await session.execute(key_stmt)
        api_key = key_result.scalars().first()
        if api_key is None:
            api_key = ApiKey(user_id=user.id, key_hash=key_hash, label="seed")
            session.add(api_key)

        await session.commit()

