from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.admin_models import (
    AddUserRequest,
    AddUserResponse,
    ApiKeyInfo,
    InspectUserRequest,
    InspectUserResponse,
    RotateKeyRequest,
    RotateKeyResponse,
)
from db.auth import require_admin_key
from db.identity_admin import (
    api_key_is_active,
    get_or_create_user,
    get_user_by_email,
    issue_api_key,
    list_api_keys_for_user,
    rotate_user_api_key,
)
from db.session import get_session

router = APIRouter(prefix="/admin", include_in_schema=False)


@router.post("/add-user", response_model=AddUserResponse)
async def admin_add_user(
    body: AddUserRequest,
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> AddUserResponse:
    user, created = await get_or_create_user(session, body.email)
    if not created:
        raise HTTPException(status_code=409, detail="User already exists")
    api_key = await issue_api_key(
        session,
        user.id,
        expires_at=body.expires_at,
        label="admin-add-user",
    )
    return AddUserResponse(
        user_id=user.id,
        email=user.email,
        api_key=api_key,
        created=created,
        expires_at=body.expires_at,
    )


@router.post("/rotate-key", response_model=RotateKeyResponse)
async def admin_rotate_key(
    body: RotateKeyRequest,
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> RotateKeyResponse:
    user = await get_user_by_email(session, body.email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    api_key = await rotate_user_api_key(
        session,
        user.id,
        expires_at=body.expires_at,
        label="admin-rotate-key",
    )
    return RotateKeyResponse(
        user_id=user.id,
        email=user.email,
        api_key=api_key,
        expires_at=body.expires_at,
    )


@router.post("/inspect-user", response_model=InspectUserResponse)
async def admin_inspect_user(
    body: InspectUserRequest,
    _: None = Depends(require_admin_key),
    session: AsyncSession = Depends(get_session),
) -> InspectUserResponse:
    user = await get_user_by_email(session, body.email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    keys = await list_api_keys_for_user(session, user.id)
    return InspectUserResponse(
        user_id=user.id,
        email=user.email,
        api_keys=[
            ApiKeyInfo(
                id=key.id,
                label=key.label,
                created_at=key.created_at,
                expires_at=key.expires_at,
                revoked_at=key.revoked_at,
                is_active=api_key_is_active(key),
            )
            for key in keys
        ],
    )
