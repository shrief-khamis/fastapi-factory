from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"


class SleepResponse(BaseModel):
    status: str = "ok"
    slept_seconds: float

