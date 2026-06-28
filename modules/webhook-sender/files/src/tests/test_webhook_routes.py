"""API tests for webhook job submission route."""

from unittest.mock import MagicMock, patch


async def test_submit_job_with_webhook_returns_job_id(client) -> None:
    mock_result = MagicMock()
    mock_result.id = "test-job-id-123"

    with (
        patch(
            "api.routes.webhook_routes.run_work_with_webhook.delay",
            return_value=mock_result,
        ),
        patch("api.routes.webhook_routes.job_register"),
    ):
        response = await client.post(
            "/submit-job-with-webhook",
            json={
                "data": "payload",
                "webhook_url": "https://example.com/hook",
            },
        )

    assert response.status_code == 200
    assert response.json()["job_id"] == "test-job-id-123"


async def test_submit_job_with_webhook_invalid_url_returns_422(client) -> None:
    response = await client.post(
        "/submit-job-with-webhook",
        json={"data": "payload", "webhook_url": "not-a-valid-url"},
    )
    assert response.status_code == 422
