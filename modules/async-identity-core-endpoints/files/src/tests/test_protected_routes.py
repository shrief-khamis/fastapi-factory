"""API tests for identity-protected routes."""

from conftest_db import TEST_API_KEY, TEST_USER_EMAIL, TEST_USER_ID


async def test_protected_me_without_api_key_returns_401(db_client) -> None:
    response = await db_client.get("/protected/me")
    assert response.status_code == 401


async def test_protected_me_with_invalid_api_key_returns_401(db_client) -> None:
    response = await db_client.get(
        "/protected/me",
        headers={"X-API-Key": "not-a-valid-key"},
    )
    assert response.status_code == 401


async def test_protected_me_with_valid_api_key_returns_user(db_client, auth_headers) -> None:
    response = await db_client.get("/protected/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == TEST_USER_ID
    assert data["email"] == TEST_USER_EMAIL


async def test_protected_me_seed_key_string(db_client) -> None:
    response = await db_client.get(
        "/protected/me",
        headers={"X-API-Key": TEST_API_KEY},
    )
    assert response.status_code == 200
