from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"


class WebhookPayload(BaseModel):
    """
    Generic payload for incoming webhooks.

    You can customize this model in your generated project to better match
    the shape of the callbacks you expect.
    """

    job_id: str | None = None
    status: str | None = None
    result: dict | None = None

