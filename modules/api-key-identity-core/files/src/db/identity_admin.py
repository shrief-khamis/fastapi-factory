from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.auth import generate_api_key, hash_api_key
from db.config import get_settings
from db.models import ApiKey, User


def _is_active(key: ApiKey, *, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    if key.revoked_at is not None:
        return False
    if key.expires_at is not None and key.expires_at <= now:
        return False
    return True


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email).limit(1)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_or_create_user(session: AsyncSession, email: str) -> tuple[User, bool]:
    user = await get_user_by_email(session, email)
    if user is not None:
        return user, False
    user = User(id=str(uuid.uuid4()), email=email)
    session.add(user)
    await session.flush()
    return user, True


async def issue_api_key(
    session: AsyncSession,
    user_id: str,
    *,
    expires_at: datetime | None = None,
    label: str | None = "admin-issued",
) -> str:
    """Issue a new API key without revoking existing active keys."""
    settings = get_settings()
    plaintext = generate_api_key()
    session.add(
        ApiKey(
            user_id=user_id,
            key_hash=hash_api_key(plaintext, salt=settings.API_KEY_SALT),
            label=label,
            expires_at=expires_at,
        )
    )
    await session.commit()
    return plaintext


async def rotate_user_api_key(
    session: AsyncSession,
    user_id: str,
    *,
    expires_at: datetime | None = None,
    label: str | None = "admin-issued",
) -> str:
    """Revoke all active keys and issue a new one in a single transaction."""
    now = datetime.now(timezone.utc)
    stmt = select(ApiKey).where(
        ApiKey.user_id == user_id,
        ApiKey.revoked_at.is_(None),
        or_(ApiKey.expires_at.is_(None), ApiKey.expires_at > now),
    )
    result = await session.execute(stmt)
    for key in result.scalars().all():
        key.revoked_at = now

    settings = get_settings()
    plaintext = generate_api_key()
    session.add(
        ApiKey(
            user_id=user_id,
            key_hash=hash_api_key(plaintext, salt=settings.API_KEY_SALT),
            label=label,
            expires_at=expires_at,
        )
    )
    await session.commit()
    return plaintext


async def list_api_keys_for_user(session: AsyncSession, user_id: str) -> list[ApiKey]:
    stmt = (
        select(ApiKey)
        .where(ApiKey.user_id == user_id)
        .order_by(ApiKey.created_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


def api_key_is_active(key: ApiKey) -> bool:
    return _is_active(key)
