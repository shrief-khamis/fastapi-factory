import os

import httpx

from core.celery_app import celery_app
from engine.work import do_work


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
)
def run_work_with_webhook(self, payload: dict) -> dict:
    """
    Execute the work and, if a webhook_url is present in the payload,
    enqueue a separate task to deliver the result to that webhook.
    """
    job_payload = payload.get("data")
    webhook_url = payload.get("webhook_url")

    result = do_work(job_payload)

    if webhook_url:
        deliver_webhook.delay(
            webhook_url=webhook_url,
            job_id=self.request.id,
            status="SUCCESS",
            result=result,
        )

    return result


@celery_app.task(
    bind=True,
    autoretry_for=(httpx.RequestError, httpx.HTTPStatusError),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=int(os.getenv("WEBHOOK_MAX_RETRIES", "5")),
)
def deliver_webhook(self, webhook_url: str, job_id: str, status: str, result: dict | None) -> None:
    timeout = int(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "10"))
    payload = {
        "job_id": job_id,
        "status": status,
        "result": result,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(webhook_url, json=payload)
        resp.raise_for_status()

