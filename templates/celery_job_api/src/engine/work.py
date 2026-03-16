"""Actual work executed by the Celery task. Dummy implementation."""
import time


def do_work(payload: dict) -> dict:
    """Heavy or long-running work. Called by the worker, not by the API."""
    # Dummy: echo payload and a simple result
    time.sleep(20)
    return {"received": payload, "result": "done"}

