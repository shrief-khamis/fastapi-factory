from fastapi import APIRouter, Depends

from api.models import ProtectedMeResponse
from db.auth import get_current_user

router = APIRouter()


@router.get("/protected/me", response_model=ProtectedMeResponse)
async def protected_me(user=Depends(get_current_user)) -> ProtectedMeResponse:
    return ProtectedMeResponse(user_id=user.id, email=user.email)
