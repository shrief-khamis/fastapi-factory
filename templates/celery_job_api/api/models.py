from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"


class HealthReadyResponse(BaseModel):
    """Readiness: app and dependencies (e.g. Redis) are up."""

    status: str = "ok"
    redis: str = "up"


class SubmitJobRequest(BaseModel):
    """Payload for POST /jobs. Customize as needed."""

    data: str | None = None


class SubmitJobResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE


class JobResultResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None  # present when status is SUCCESS
