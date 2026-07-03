"""Unit tests for usage admin DB helpers."""

from db.usage_admin import list_endpoint_pricing, upsert_endpoint_pricing


async def test_upsert_endpoint_pricing_creates_row(seeded_db) -> None:
    row, created = await upsert_endpoint_pricing(
        seeded_db,
        "test.metered",
        3,
    )
    assert created is True
    assert row.endpoint_key == "test.metered"
    assert row.usage_units == 3


async def test_upsert_endpoint_pricing_updates_row(seeded_db) -> None:
    await upsert_endpoint_pricing(seeded_db, "test.metered", 2)

    row, created = await upsert_endpoint_pricing(
        seeded_db,
        "test.metered",
        7,
    )
    assert created is False
    assert row.usage_units == 7


async def test_list_endpoint_pricing_returns_sorted_rows(seeded_db) -> None:
    await upsert_endpoint_pricing(seeded_db, "z.endpoint", 1)
    await upsert_endpoint_pricing(seeded_db, "a.endpoint", 2)

    rows = await list_endpoint_pricing(seeded_db)
    assert [row.endpoint_key for row in rows] == ["a.endpoint", "z.endpoint"]
