import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_webhook_endpoint_accepts_payload(client: AsyncClient):
    payload = {"job_id": "123", "status": "SUCCESS", "result": {"value": 42}}
    response = await client.post("/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

