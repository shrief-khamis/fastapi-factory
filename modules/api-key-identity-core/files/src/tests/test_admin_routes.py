"""API tests for admin identity routes."""

from datetime import datetime, timedelta, timezone


async def test_admin_add_user_without_admin_key_returns_401(db_client) -> None:
    response = await db_client.post(
        "/admin/add-user",
        json={"email": "new@example.com"},
    )
    assert response.status_code == 401


async def test_admin_add_user_with_invalid_admin_key_returns_401(db_client) -> None:
    response = await db_client.post(
        "/admin/add-user",
        json={"email": "new@example.com"},
        headers={"X-Admin-Key": "wrong-admin-key"},
    )
    assert response.status_code == 401


async def test_admin_add_user_creates_user_and_returns_api_key(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/add-user",
        json={"email": "newuser@example.com"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["created"] is True
    assert data["user_id"]
    assert data["api_key"]
    assert len(data["api_key"]) > 20

    me = await db_client.get(
        "/protected/me",
        headers={"X-API-Key": data["api_key"]},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "newuser@example.com"


async def test_admin_add_user_with_expiry(db_client, admin_headers) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    response = await db_client.post(
        "/admin/add-user",
        json={
            "email": "new-expiry@example.com",
            "expires_at": expires_at.isoformat(),
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["expires_at"] is not None


async def test_admin_add_user_existing_email_returns_409(
    db_client,
    admin_headers,
) -> None:
    first = await db_client.post(
        "/admin/add-user",
        json={"email": "repeat@example.com"},
        headers=admin_headers,
    )
    assert first.status_code == 200
    assert first.json()["created"] is True
    first_key = first.json()["api_key"]

    second = await db_client.post(
        "/admin/add-user",
        json={"email": "repeat@example.com"},
        headers=admin_headers,
    )
    assert second.status_code == 409
    assert second.json()["detail"] == "User already exists"

    me = await db_client.get(
        "/protected/me",
        headers={"X-API-Key": first_key},
    )
    assert me.status_code == 200


async def test_admin_rotate_key_user_not_found_returns_404(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/rotate-key",
        json={"email": "missing@example.com"},
        headers=admin_headers,
    )
    assert response.status_code == 404


async def test_admin_rotate_key_rotates_active_key(
    db_client,
    admin_headers,
) -> None:
    created = await db_client.post(
        "/admin/add-user",
        json={"email": "rotate@example.com"},
        headers=admin_headers,
    )
    old_key = created.json()["api_key"]

    rotated = await db_client.post(
        "/admin/rotate-key",
        json={"email": "rotate@example.com"},
        headers=admin_headers,
    )
    assert rotated.status_code == 200
    new_key = rotated.json()["api_key"]
    assert new_key != old_key

    old_me = await db_client.get("/protected/me", headers={"X-API-Key": old_key})
    assert old_me.status_code == 401

    new_me = await db_client.get("/protected/me", headers={"X-API-Key": new_key})
    assert new_me.status_code == 200


async def test_admin_rotate_key_with_expiry(db_client, admin_headers) -> None:
    await db_client.post(
        "/admin/add-user",
        json={"email": "expiry@example.com"},
        headers=admin_headers,
    )
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    response = await db_client.post(
        "/admin/rotate-key",
        json={
            "email": "expiry@example.com",
            "expires_at": expires_at.isoformat(),
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["expires_at"] is not None


async def test_admin_inspect_user_returns_key_metadata(
    db_client,
    admin_headers,
) -> None:
    created = await db_client.post(
        "/admin/add-user",
        json={"email": "inspect@example.com"},
        headers=admin_headers,
    )
    assert created.status_code == 200

    response = await db_client.post(
        "/admin/inspect-user",
        json={"email": "inspect@example.com"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "inspect@example.com"
    assert len(data["api_keys"]) >= 1
    key_info = data["api_keys"][0]
    assert "id" in key_info
    assert "created_at" in key_info
    assert "is_active" in key_info
    assert "api_key" not in key_info


async def test_admin_inspect_user_not_found_returns_404(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/inspect-user",
        json={"email": "nobody@example.com"},
        headers=admin_headers,
    )
    assert response.status_code == 404


async def test_admin_routes_not_in_openapi_schema(db_client) -> None:
    response = await db_client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/admin/add-user" not in paths
    assert "/admin/rotate-key" not in paths
    assert "/admin/inspect-user" not in paths


async def test_admin_unconfigured_returns_503(db_client, monkeypatch) -> None:
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    from db.config import get_settings

    get_settings.cache_clear()

    response = await db_client.post(
        "/admin/add-user",
        json={"email": "x@example.com"},
        headers={"X-Admin-Key": "any"},
    )
    assert response.status_code == 503

    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key-for-pytest")
    get_settings.cache_clear()
