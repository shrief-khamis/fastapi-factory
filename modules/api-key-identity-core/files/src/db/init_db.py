from __future__ import annotations

from db.base import Base
from db.session import get_engine


async def create_schema() -> None:
    """
    Create tables directly from SQLAlchemy metadata.

    This is primarily for tests and local/dev convenience.
    Production migrations should be run via Alembic.
    """

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

