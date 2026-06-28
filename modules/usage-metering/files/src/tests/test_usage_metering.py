"""Unit tests for usage metering DB helpers."""

from conftest_db import TEST_USER_ID
from seed_usage import seed_usage_pricing
from db.usage_metering import record_usage_event_if_metered, resolve_usage_units
from db.usage_models import UsageEvent
from sqlalchemy import func, select


async def test_resolve_usage_units_returns_none_for_unknown_endpoint(seeded_db) -> None:
    units = await resolve_usage_units(seeded_db, "unknown.endpoint")
    assert units is None


async def test_resolve_usage_units_returns_configured_units(seeded_db) -> None:
    await seed_usage_pricing(
        seeded_db, endpoint_key="test.metered", usage_units=3
    )
    units = await resolve_usage_units(seeded_db, "test.metered")
    assert units == 3


async def test_record_usage_event_inserts_row_when_metered(seeded_db) -> None:
    await seed_usage_pricing(
        seeded_db, endpoint_key="test.metered", usage_units=2
    )

    inserted = await record_usage_event_if_metered(
        seeded_db,
        user_id=TEST_USER_ID,
        endpoint_key="test.metered",
    )
    assert inserted is True

    count = await seeded_db.scalar(select(func.count()).select_from(UsageEvent))
    assert count == 1


async def test_record_usage_event_no_op_when_not_metered(seeded_db) -> None:
    inserted = await record_usage_event_if_metered(
        seeded_db,
        user_id=TEST_USER_ID,
        endpoint_key="unpriced.endpoint",
    )
    assert inserted is False

    count = await seeded_db.scalar(select(func.count()).select_from(UsageEvent))
    assert count == 0
