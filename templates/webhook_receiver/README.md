# Webhook Receiver API

FastAPI service with a single inbound webhook endpoint. Payloads are passed to **`src/engine/processor.py`** — replace `process_webhook()` with your logic (the default just logs).

## Quick run

```bash
cp .env.example .env   # optional
docker compose up --build
```

API: `http://localhost:8001` · OpenAPI docs: `http://localhost:8001/docs`

Without Docker:

```bash
pip install -r requirements.txt
cd src && uvicorn main:app --reload --port 8001
```

## Add your code

Implement **`src/engine/processor.py`** — `process_webhook(payload)` runs on each `POST /webhook`. Adjust validation or routing in `src/api/routes.py` if needed.

## Optional modules

This template does not support optional modules. It was generated as a standalone receiver. For outbound webhook delivery on job completion, use the `celery_job_api` template with the `webhook_sender` module instead.

## Base endpoint

- `POST /webhook` — accepts JSON, hands off to the engine

## Tests

```bash
pip install -r requirements.txt
cd src && pytest -v
```
