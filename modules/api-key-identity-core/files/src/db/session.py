from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.config import get_settings


@lru_cache
def get_engine():
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )


@lru_cache
def get_sessionmaker():
    return async_sessionmaker(
        get_engine(),
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = get_sessionmaker()
    # `sessionmaker` is a factory; call it to get an AsyncSession instance.
    async with sessionmaker() as session:
        yield session

