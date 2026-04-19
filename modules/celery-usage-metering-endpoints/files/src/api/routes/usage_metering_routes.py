from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import (
    JobResultResponse,
    JobStatusResponse,
    SubmitJobRequest,
    SubmitJobResponse,
)
from core.job_registry_identity import exists_for_user as job_exists_for_user
from core.job_registry_identity import register as job_register
from core.tasks import run_work
from db.auth import get_current_user
from db.session import get_session
from db.usage_metering import record_usage_event_if_metered

router = APIRouter()


@router.post(
    "/metered/submit-job",
    response_model=SubmitJobResponse,
)
async def metered_submit_job(
    body: SubmitJobRequest,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SubmitJobResponse:
    payload = body.model_dump()
    task = run_work.delay(payload)
    job_register(task.id, user.id)
    await record_usage_event_if_metered(
        session,
        user_id=user.id,
        endpoint_key="celery.metered_submit_job",
    )
    return SubmitJobResponse(job_id=task.id)


@router.get("/metered/job-status/{job_id}", response_model=JobStatusResponse)
async def metered_get_job_status(
    job_id: str,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> JobStatusResponse:
    if not job_exists_for_user(job_id, user.id):
        raise HTTPException(status_code=404, detail="Job not found")
    await record_usage_event_if_metered(
        session,
        user_id=user.id,
        endpoint_key="celery.metered_job_status",
    )
    result = AsyncResult(job_id, app=run_work.app)
    return JobStatusResponse(job_id=job_id, status=result.status)


@router.get("/metered/job-results/{job_id}", response_model=JobResultResponse)
async def metered_get_job_result(
    job_id: str,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> JobResultResponse:
    if not job_exists_for_user(job_id, user.id):
        raise HTTPException(status_code=404, detail="Job not found")
    await record_usage_event_if_metered(
        session,
        user_id=user.id,
        endpoint_key="celery.metered_job_result",
    )
    result = AsyncResult(job_id, app=run_work.app)
    if result.status == "PENDING" or result.status == "STARTED":
        raise HTTPException(status_code=202, detail="Job not ready")
    if result.status == "FAILURE":
        return JobResultResponse(job_id=job_id, status="FAILURE", result=None)
    return JobResultResponse(
        job_id=job_id, status=result.status, result=result.result
    )
