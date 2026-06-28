"""API tests for metered async routes."""

from unittest.mock import AsyncMock, patch


async def test_metered_sleep_without_api_key_returns_401(db_client) -> None:
    response = await db_client.get("/metered/sleep")
    assert response.status_code == 401


async def test_metered_sleep_with_valid_api_key_returns_200(
    db_client,
    auth_headers,
) -> None:
    with patch(
        "api.routes.base_routes.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        response = await db_client.get("/metered/sleep", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["slept_seconds"] == 10.0
