"""Test helpers for usage metering (copied by usage_metering module)."""

from __future__ import annotations


async def seed_usage_pricing(session, *, endpoint_key: str, usage_units: int) -> None:
    from db.usage_models import UsageEndpointPricing

    session.add(
        UsageEndpointPricing(endpoint_key=endpoint_key, usage_units=usage_units)
    )
    await session.commit()
