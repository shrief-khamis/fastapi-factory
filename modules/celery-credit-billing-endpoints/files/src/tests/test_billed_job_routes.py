"""API tests for billed Celery job routes (auth wiring)."""

async def test_billed_submit_job_without_api_key_returns_401(db_client) -> None:
    response = await db_client.post("/billed/submit-job", json={"data": "hello"})
    assert response.status_code == 401


async def test_billed_job_status_without_api_key_returns_401(db_client) -> None:
    response = await db_client.get("/billed/job-status/some-job-id")
    assert response.status_code == 401
