from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.usage_models import UsageEndpointPricing


async def get_endpoint_pricing(
    session: AsyncSession, endpoint_key: str
) -> UsageEndpointPricing | None:
    stmt = (
        select(UsageEndpointPricing)
        .where(UsageEndpointPricing.endpoint_key == endpoint_key)
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def upsert_endpoint_pricing(
    session: AsyncSession,
    endpoint_key: str,
    usage_units: int,
) -> tuple[UsageEndpointPricing, bool]:
    """Create or update endpoint pricing. Returns (row, created)."""
    row = await get_endpoint_pricing(session, endpoint_key)
    if row is None:
        row = UsageEndpointPricing(
            endpoint_key=endpoint_key,
            usage_units=usage_units,
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return row, True

    row.usage_units = usage_units
    await session.commit()
    await session.refresh(row)
    return row, False


async def list_endpoint_pricing(session: AsyncSession) -> list[UsageEndpointPricing]:
    stmt = select(UsageEndpointPricing).order_by(UsageEndpointPricing.endpoint_key)
    result = await session.execute(stmt)
    return list(result.scalars().all())
