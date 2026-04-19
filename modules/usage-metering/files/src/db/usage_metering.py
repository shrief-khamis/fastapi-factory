from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.usage_models import UsageEndpointPricing, UsageEvent


async def resolve_usage_units(
    session: AsyncSession, endpoint_key: str
) -> int | None:
    """
    Resolve usage units for an endpoint key.

    Returns None when endpoint_key is not configured (endpoint is not metered).
    """
    stmt = (
        select(UsageEndpointPricing.usage_units)
        .where(UsageEndpointPricing.endpoint_key == endpoint_key)
        .limit(1)
    )
    result = await session.execute(stmt)
    units = result.scalar_one_or_none()
    return units


async def record_usage_event_if_metered(
    session: AsyncSession,
    *,
    user_id: str,
    endpoint_key: str,
) -> bool:
    """
    Insert a usage event if the endpoint has pricing configured.

    Returns:
      - True: event was inserted
      - False: endpoint is not metered (no pricing row)
    """
    usage_units = await resolve_usage_units(session, endpoint_key)
    if usage_units is None:
        return False
    session.add(
        UsageEvent(
            user_id=user_id,
            endpoint_key=endpoint_key,
            usage_units=usage_units,
        )
    )
    await session.commit()
    return True
