from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import SleepResponse
from api.routes.base_routes import sleep as base_sleep
from db.auth import get_current_user
from db.session import get_session
from db.usage_metering import record_usage_event_if_metered

router = APIRouter()


@router.get("/metered/sleep", response_model=SleepResponse)
async def metered_sleep(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SleepResponse:
    endpoint_key = "async.metered_sleep"
    await record_usage_event_if_metered(
        session,
        user_id=user.id,
        endpoint_key=endpoint_key,
    )
    return await base_sleep()
