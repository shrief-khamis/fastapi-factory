import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_submit_job_returns_job_id(client: AsyncClient):
    response = await client.post("/submit-job", json={"data": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)
    assert len(data["job_id"]) > 0


@pytest.mark.asyncio
async def test_job_status_unknown_id_returns_404(client: AsyncClient):
    response = await client.get("/job-status/unknown-job-id-12345")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_job_status_known_id_returns_pending(client: AsyncClient):
    submit = await client.post("/submit-job", json={})
    assert submit.status_code == 200
    job_id = submit.json()["job_id"]
    response = await client.get(f"/job-status/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_job_results_unknown_id_returns_404(client: AsyncClient):
    response = await client.get("/job-results/unknown-job-id-12345")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

