from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException

from api.models import JobResultResponse, JobStatusResponse, SubmitJobRequest, SubmitJobResponse
from core.job_registry_identity import exists_for_user as job_exists_for_user
from core.job_registry_identity import register as job_register
from core.tasks import run_work
from db.auth import get_current_user
from utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/identity/submit-job", response_model=SubmitJobResponse)
async def submit_identity_job(
    body: SubmitJobRequest,
    user=Depends(get_current_user),
) -> SubmitJobResponse:
    payload = body.model_dump()
    task = run_work.delay(payload)
    job_register(task.id, user.id)
    logger.debug("identity job submitted: job_id=%s user_id=%s", task.id, user.id)
    return SubmitJobResponse(job_id=task.id)


@router.get("/identity/job-status/{job_id}", response_model=JobStatusResponse)
async def get_identity_job_status(
    job_id: str,
    user=Depends(get_current_user),
) -> JobStatusResponse:
    if not job_exists_for_user(job_id, user.id):
        raise HTTPException(status_code=404, detail="Job not found")
    result = AsyncResult(job_id, app=run_work.app)
    return JobStatusResponse(job_id=job_id, status=result.status)


@router.get("/identity/job-results/{job_id}", response_model=JobResultResponse)
async def get_identity_job_result(
    job_id: str,
    user=Depends(get_current_user),
) -> JobResultResponse:
    if not job_exists_for_user(job_id, user.id):
        raise HTTPException(status_code=404, detail="Job not found")
    result = AsyncResult(job_id, app=run_work.app)
    if result.status == "PENDING" or result.status == "STARTED":
        raise HTTPException(status_code=202, detail="Job not ready")
    if result.status == "FAILURE":
        return JobResultResponse(job_id=job_id, status="FAILURE", result=None)
    return JobResultResponse(
        job_id=job_id, status=result.status, result=result.result
    )
