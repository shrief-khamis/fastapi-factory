"""API tests for billed async routes."""

from unittest.mock import AsyncMock, patch

from conftest_db import TEST_USER_ID
from seed_credit import seed_credit_balance
from seed_usage import seed_usage_pricing


async def test_billed_sleep_without_api_key_returns_401(db_client) -> None:
    response = await db_client.get("/billed/sleep")
    assert response.status_code == 401


async def test_billed_sleep_with_insufficient_credits_returns_402(
    db_client,
    auth_headers,
) -> None:
    from db.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        await seed_usage_pricing(
            session, endpoint_key="async.billed_sleep", usage_units=5
        )
        await seed_credit_balance(session, user_id=TEST_USER_ID, units=1)

    response = await db_client.get("/billed/sleep", headers=auth_headers)
    assert response.status_code == 402


async def test_billed_sleep_with_sufficient_credits_returns_200(
    db_client,
    auth_headers,
) -> None:
    from db.session import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        await seed_usage_pricing(
            session, endpoint_key="async.billed_sleep", usage_units=3
        )
        await seed_credit_balance(session, user_id=TEST_USER_ID, units=10)

    with patch(
        "api.routes.base_routes.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        response = await db_client.get("/billed/sleep", headers=auth_headers)
    assert response.status_code == 200
