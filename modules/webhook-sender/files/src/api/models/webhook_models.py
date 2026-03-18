from pydantic import BaseModel, HttpUrl


class SubmitJobWithWebhookRequest(BaseModel):
    """Payload for POST /submit-job-with-webhook."""

    data: str | None = None
    webhook_url: HttpUrl | None = None

