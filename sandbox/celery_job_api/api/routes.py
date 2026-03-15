from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from api.models import (
    HealthReadyResponse,
    HealthResponse,
    JobResultResponse,
    JobStatusResponse,
    SubmitJobRequest,
    SubmitJobResponse,
)
from core.job_registry import exists as job_exists, register as job_register
from core.redis import ping_redis
from core.tasks import run_work
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/health/ready", response_model=HealthReadyResponse)
async def health_ready() -> HealthReadyResponse:
    """Readiness probe: returns 200 if Redis is up, 503 otherwise."""
    if not ping_redis():
        raise HTTPException(
            status_code=503,
            detail={"status": "degraded", "redis": "down"},
        )
    return HealthReadyResponse()


@router.post("/submit-job", response_model=SubmitJobResponse)
async def submit_job(body: SubmitJobRequest) -> SubmitJobResponse:
    payload = body.model_dump()
    task = run_work.delay(payload)
    job_register(task.id)
    logger.debug("job submitted: job_id=%s", task.id)
    return SubmitJobResponse(job_id=task.id)


@router.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    if not job_exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    result = AsyncResult(job_id, app=run_work.app)
    return JobStatusResponse(job_id=job_id, status=result.status)


@router.get("/job-results/{job_id}", response_model=JobResultResponse)
async def get_job_result(job_id: str) -> JobResultResponse:
    if not job_exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    result = AsyncResult(job_id, app=run_work.app)
    if result.status == "PENDING" or result.status == "STARTED":
        raise HTTPException(status_code=202, detail="Job not ready")
    if result.status == "FAILURE":
        return JobResultResponse(job_id=job_id, status="FAILURE", result=None)
    return JobResultResponse(
        job_id=job_id, status=result.status, result=result.result
    )
