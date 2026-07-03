# Celery Job API

FastAPI service that enqueues work to Celery and exposes job status/result endpoints. Redis backs the broker and a short-lived job registry.

## Quick run

```bash
cp .env.example .env
docker compose up --build
```

Starts `redis`, the `api` (port 8000), and a Celery `worker`. OpenAPI docs: `http://localhost:8000/docs`

Without Docker — API and worker in separate terminals (Redis must be running):

```bash
pip install -r requirements.txt
cp .env.example .env
cd src && uvicorn main:app --reload
```

```bash
cd src && celery -A core.celery_app worker -l info
```

## Add your code

Implement your work in **`src/engine/work.py`** — the `do_work(payload)` function is what the Celery task runs. Routes in `src/api/routes/base_routes.py` enqueue jobs; extend or add routes under `src/api/routes/` as needed.

## Optional modules

This project may have been generated with optional modules from [FastAPI Factory](https://github.com/shrief-khamis/fastapi-factory). If so, extra routes, env vars, and services were added automatically. Check the generator output for the module list, or inspect `docker-compose.yml` and `.env.example`.

Supported modules for this template: `identity_auth`, `usage_metering_auth`, `credit_billing_auth`, `webhook_sender`.

If you used `identity_auth` (or a bundle that includes it):

- **User API keys** — dev users are seeded by Alembic (`alembic/versions/0002_seed_dev_identity_data.py`). Send the key in the `X-API-Key` header.
- **Admin provisioning** — set `ADMIN_API_KEY` in `.env` and call `POST /admin/add-user` to onboard users, `POST /admin/rotate-key` to replace active keys, or `POST /admin/inspect-user` to list key metadata. Send `X-Admin-Key` on these requests. Admin routes are hidden from `/docs`.

## Base endpoints

- `GET /health`, `GET /health/ready` (Redis readiness)
- `POST /submit-job` → `job_id`
- `GET /job-status/{job_id}`
- `GET /job-results/{job_id}`

## Tests

```bash
pip install -r requirements.txt
cd src && pytest -v
```

Requires Redis (lifespan pings Redis on startup).
