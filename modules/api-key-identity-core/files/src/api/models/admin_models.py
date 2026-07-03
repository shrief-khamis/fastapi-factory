from datetime import datetime

from pydantic import BaseModel, EmailStr


class AddUserRequest(BaseModel):
    email: EmailStr
    expires_at: datetime | None = None


class AddUserResponse(BaseModel):
    user_id: str
    email: EmailStr
    api_key: str
    created: bool
    expires_at: datetime | None = None


class RotateKeyRequest(BaseModel):
    email: EmailStr
    expires_at: datetime | None = None


class RotateKeyResponse(BaseModel):
    user_id: str
    email: EmailStr
    api_key: str
    expires_at: datetime | None = None


class InspectUserRequest(BaseModel):
    email: EmailStr


class ApiKeyInfo(BaseModel):
    id: int
    label: str | None
    created_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None
    is_active: bool


class InspectUserResponse(BaseModel):
    user_id: str
    email: EmailStr
    api_keys: list[ApiKeyInfo]
