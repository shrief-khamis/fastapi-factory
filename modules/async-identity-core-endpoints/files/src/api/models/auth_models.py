from pydantic import BaseModel


class ProtectedMeResponse(BaseModel):
    user_id: str
    email: str
