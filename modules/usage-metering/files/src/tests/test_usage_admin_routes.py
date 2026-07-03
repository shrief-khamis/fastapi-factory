"""API tests for admin usage metering routes."""


async def test_admin_upsert_endpoint_pricing_without_admin_key_returns_401(
    db_client,
) -> None:
    response = await db_client.post(
        "/admin/upsert-endpoint-pricing",
        json={"endpoint_key": "test.endpoint", "usage_units": 2},
    )
    assert response.status_code == 401


async def test_admin_upsert_endpoint_pricing_with_invalid_admin_key_returns_401(
    db_client,
) -> None:
    response = await db_client.post(
        "/admin/upsert-endpoint-pricing",
        json={"endpoint_key": "test.endpoint", "usage_units": 2},
        headers={"X-Admin-Key": "wrong-admin-key"},
    )
    assert response.status_code == 401


async def test_admin_upsert_endpoint_pricing_creates_pricing(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/upsert-endpoint-pricing",
        json={"endpoint_key": "test.metered", "usage_units": 3},
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["created"] is True
    assert data["pricing"]["endpoint_key"] == "test.metered"
    assert data["pricing"]["usage_units"] == 3

    listed = await db_client.post(
        "/admin/list-endpoint-pricing",
        headers=admin_headers,
    )
    assert listed.status_code == 200
    rows = {row["endpoint_key"]: row for row in listed.json()["pricing"]}
    assert rows["test.metered"]["usage_units"] == 3


async def test_admin_upsert_endpoint_pricing_updates_existing(
    db_client,
    admin_headers,
) -> None:
    created = await db_client.post(
        "/admin/upsert-endpoint-pricing",
        json={"endpoint_key": "test.metered", "usage_units": 2},
        headers=admin_headers,
    )
    assert created.status_code == 200
    assert created.json()["created"] is True

    updated = await db_client.post(
        "/admin/upsert-endpoint-pricing",
        json={"endpoint_key": "test.metered", "usage_units": 5},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    data = updated.json()
    assert data["created"] is False
    assert data["pricing"]["usage_units"] == 5


async def test_admin_upsert_endpoint_pricing_rejects_non_positive_units(
    db_client,
    admin_headers,
) -> None:
    response = await db_client.post(
        "/admin/upsert-endpoint-pricing",
        json={"endpoint_key": "test.metered", "usage_units": 0},
        headers=admin_headers,
    )
    assert response.status_code == 422


async def test_admin_list_endpoint_pricing_returns_rows(
    db_client,
    admin_headers,
) -> None:
    await db_client.post(
        "/admin/upsert-endpoint-pricing",
        json={"endpoint_key": "alpha.endpoint", "usage_units": 1},
        headers=admin_headers,
    )
    await db_client.post(
        "/admin/upsert-endpoint-pricing",
        json={"endpoint_key": "beta.endpoint", "usage_units": 4},
        headers=admin_headers,
    )

    response = await db_client.post(
        "/admin/list-endpoint-pricing",
        headers=admin_headers,
    )
    assert response.status_code == 200
    pricing = response.json()["pricing"]
    keys = {row["endpoint_key"] for row in pricing}
    assert "alpha.endpoint" in keys
    assert "beta.endpoint" in keys


async def test_admin_usage_routes_not_in_openapi_schema(db_client) -> None:
    response = await db_client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/admin/upsert-endpoint-pricing" not in paths
    assert "/admin/list-endpoint-pricing" not in paths
