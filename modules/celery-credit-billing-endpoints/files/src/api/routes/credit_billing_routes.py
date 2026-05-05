from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import NoReturn

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
from db.credit_billing import bill_user_for_endpoint
from db.session import get_session

router = APIRouter()


def _raise_insufficient_credits(required_units: int | None) -> NoReturn:
    needed = "configured" if required_units is None else str(required_units)
    raise HTTPException(
        status_code=402,
        detail=f"Insufficient credits for endpoint, requires {needed} units.",
    )


@router.post("/billed/submit-job", response_model=SubmitJobResponse)
async def billed_submit_job(
    body: SubmitJobRequest,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SubmitJobResponse:
    billed, required_units = await bill_user_for_endpoint(
        session,
        user_id=user.id,
        endpoint_key="celery.billed_submit_job",
    )
    if not billed:
        _raise_insufficient_credits(required_units)

    payload = body.model_dump()
    task = run_work.delay(payload)
    job_register(task.id, user.id)
    return SubmitJobResponse(job_id=task.id)


@router.get("/billed/job-status/{job_id}", response_model=JobStatusResponse)
async def billed_get_job_status(
    job_id: str,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> JobStatusResponse:
    if not job_exists_for_user(job_id, user.id):
        raise HTTPException(status_code=404, detail="Job not found")

    billed, required_units = await bill_user_for_endpoint(
        session,
        user_id=user.id,
        endpoint_key="celery.billed_job_status",
        ref=job_id,
    )
    if not billed:
        _raise_insufficient_credits(required_units)

    result = AsyncResult(job_id, app=run_work.app)
    return JobStatusResponse(job_id=job_id, status=result.status)


@router.get("/billed/job-results/{job_id}", response_model=JobResultResponse)
async def billed_get_job_result(
    job_id: str,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> JobResultResponse:
    if not job_exists_for_user(job_id, user.id):
        raise HTTPException(status_code=404, detail="Job not found")

    billed, required_units = await bill_user_for_endpoint(
        session,
        user_id=user.id,
        endpoint_key="celery.billed_job_result",
        ref=job_id,
    )
    if not billed:
        _raise_insufficient_credits(required_units)

    result = AsyncResult(job_id, app=run_work.app)
    if result.status == "PENDING" or result.status == "STARTED":
        raise HTTPException(status_code=202, detail="Job not ready")
    if result.status == "FAILURE":
        return JobResultResponse(job_id=job_id, status="FAILURE", result=None)
    return JobResultResponse(
        job_id=job_id,
        status=result.status,
        result=result.result,
    )
