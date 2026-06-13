# Async I/O API

FastAPI service with async request/response endpoints. Ships with a health check and a demo `/sleep` route — add your own routes and wire them in `src/api/routes/`.

## Quick run

```bash
cp .env.example .env   # optional
docker compose up --build
```

API: `http://localhost:8000` · OpenAPI docs: `http://localhost:8000/docs`

Without Docker:

```bash
pip install -r requirements.txt
cd src && uvicorn main:app --reload
```

## Add your code

- **Routes** — add files under `src/api/routes/`, then include them in `src/api/routes/__init__.py`
- **Models** — add Pydantic models under `src/api/models/`
- **Business logic** — keep route handlers thin; put real work in `src/` modules as needed (no separate engine file in this template)

## Optional modules

This project may have been generated with optional modules from [FastAPI Factory](https://github.com/shrief-khamis/fastapi-factory). If so, extra routes, env vars, and services (e.g. Postgres) were added automatically. Check the generator output for the module list, or inspect `docker-compose.yml` and `.env.example`.

Supported modules for this template: `identity_auth`, `usage_metering_auth`, `credit_billing_auth`.

If you used `identity_auth` (or a bundle that includes it), dev API keys are seeded by Alembic — see `alembic/versions/0002_seed_dev_identity_data.py`. Send the key in the `X-API-Key` header.

## Base endpoints

- `GET /health`
- `GET /sleep` — demo async endpoint (sleeps 10s)

## Tests

```bash
pip install -r requirements.txt
cd src && pytest -v
```
