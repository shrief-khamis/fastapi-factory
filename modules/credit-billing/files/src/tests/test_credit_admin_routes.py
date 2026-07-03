"""API tests for admin credit billing routes (auth, validation, HTTP wiring)."""

from conftest_db import TEST_USER_EMAIL


async def test_admin_inspect_credit_balance_without_admin_key_returns_401(
    db_client,
) -> None:
    response = await db_client.post(
        "/admin/inspect-credit-balance",
        json={"email": TEST_USER_EMAIL},
    )
    assert response.status_code == 401


async def test_admin_inspect_credit_balance_with_invalid_admin_key_returns_401(
    db_client,
) -> None:
    response = await db_client.post(
        "/admin/inspect-credit-balance",
        json={"email": TEST_USER_EMAIL},
        headers={"X-Admin-Key": "wrong-admin-key"},
    )
    assert response.status_code == 401


async def test_admin_inspect_credit_balance_user_not_found_returns_404(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/inspect-credit-balance",
        json={"email": "missing@example.com"},
        headers=admin_headers,
    )
    assert response.status_code == 404


async def test_admin_add_credit_user_not_found_returns_404(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/add-credit",
        json={"email": "missing@example.com", "units": 5},
        headers=admin_headers,
    )
    assert response.status_code == 404


async def test_admin_deduct_credit_user_not_found_returns_404(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/deduct-credit",
        json={"email": "missing@example.com", "units": 1},
        headers=admin_headers,
    )
    assert response.status_code == 404


async def test_admin_add_credit_happy_path(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/add-credit",
        json={"email": TEST_USER_EMAIL, "units": 12},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["added_units"] == 12
    assert data["balance"] == 12


async def test_admin_deduct_credit_rejects_non_positive_units(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/deduct-credit",
        json={"email": TEST_USER_EMAIL, "units": 0},
        headers=admin_headers,
    )
    assert response.status_code == 422


async def test_admin_list_top_credit_balances_returns_200(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/list-top-credit-balances",
        json={"limit": 5},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["balances"] == []


async def test_admin_credit_routes_not_in_openapi_schema(db_client) -> None:
    response = await db_client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/admin/inspect-credit-balance" not in paths
    assert "/admin/add-credit" not in paths
    assert "/admin/deduct-credit" not in paths
    assert "/admin/list-top-credit-balances" not in paths
