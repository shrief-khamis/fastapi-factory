from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import SleepResponse
from api.routes.base_routes import sleep as base_sleep
from db.auth import get_current_user
from db.credit_billing import bill_user_for_endpoint
from db.session import get_session

router = APIRouter()


@router.get("/billed/sleep", response_model=SleepResponse)
async def billed_sleep(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SleepResponse:
    billed, required_units = await bill_user_for_endpoint(
        session,
        user_id=user.id,
        endpoint_key="async.billed_sleep",
    )
    if not billed:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits for endpoint, requires {required_units} units.",
        )
    return await base_sleep()
