from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.config import get_settings
from db.models import ApiKey, User
from db.session import get_session


def generate_api_key() -> str:
    """Return a new random API key (plaintext; store only the hash)."""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str, *, salt: str) -> str:
    """
    Hash API keys before storing/looking them up.

    Note: We hash (not encrypt) because lookups need determinism.
    """

    raw = f"{salt}:{api_key}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


async def require_admin_key(
    admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
) -> None:
    """Validate the operator key from X-Admin-Key (separate from user X-API-Key)."""
    settings = get_settings()
    if not settings.ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail="Admin API is not configured")
    if not admin_key:
        raise HTTPException(status_code=401, detail="Missing X-Admin-Key header")
    if not secrets.compare_digest(admin_key, settings.ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid admin API key")


async def get_current_user(
    api_key: str | None = Header(default=None, alias="X-API-Key"),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    settings = get_settings()
    key_hash = hash_api_key(api_key, salt=settings.API_KEY_SALT)
    now = datetime.now(timezone.utc)

    # IMPORTANT: return `User` directly so we don't rely on lazy-loading
    # relationships (which can trigger MissingGreenlet in async SQLAlchemy).
    stmt = (
        select(User)
        .join(ApiKey, ApiKey.user_id == User.id)
        .where(
            ApiKey.key_hash == key_hash,
            ApiKey.revoked_at.is_(None),
            or_(ApiKey.expires_at.is_(None), ApiKey.expires_at > now),
        )
        .limit(1)
    )

    result = await session.execute(stmt)
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user
