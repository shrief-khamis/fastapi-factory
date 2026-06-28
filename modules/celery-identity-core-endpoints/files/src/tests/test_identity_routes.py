"""API tests for identity-protected Celery job routes (auth wiring)."""

async def test_identity_submit_job_without_api_key_returns_401(db_client) -> None:
    response = await db_client.post("/identity/submit-job", json={"data": "hello"})
    assert response.status_code == 401


async def test_identity_job_status_without_api_key_returns_401(db_client) -> None:
    response = await db_client.get("/identity/job-status/some-job-id")
    assert response.status_code == 401
