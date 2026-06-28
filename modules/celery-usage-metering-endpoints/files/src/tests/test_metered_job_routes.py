"""API tests for metered Celery job routes (auth wiring)."""

async def test_metered_submit_job_without_api_key_returns_401(db_client) -> None:
    response = await db_client.post("/metered/submit-job", json={"data": "hello"})
    assert response.status_code == 401


async def test_metered_job_status_without_api_key_returns_401(db_client) -> None:
    response = await db_client.get("/metered/job-status/some-job-id")
    assert response.status_code == 401
