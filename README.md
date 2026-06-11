# FastAPI Factory

A personal boilerplate generator for FastAPI projects. Pick a base template, optionally bolt on modules (auth, metering, billing, webhooks), and get a runnable project where the only thing left to write is the **engine** — the code that does the actual work.

## Quick start

From this repo:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generate a project:

```bash
python scripts/new_project.py \
  --template celery_job_api \
  --name my-api \
  --path ./out
```

With optional modules (comma-separated):

```bash
python scripts/new_project.py \
  --template celery_job_api \
  --name my-api \
  --path ./out \
  --modules identity_auth,webhook_sender
```

The generator copies the template to `{path}/{name}`, applies any selected modules, and prints the destination. It does not rename packages or substitute project names inside files — only the output directory name changes.

## Templates

| Template | Use when | Base stack | Default port |
|---|---|---|---|
| `async_io_api` | Request/response APIs with async endpoints (no background jobs) | FastAPI, uvicorn | 8000 |
| `celery_job_api` | Submit work as jobs; poll status/results or deliver via webhook | FastAPI, Celery, Redis | 8000 |
| `webhook_receiver` | Receive inbound HTTP callbacks and hand them to your engine | FastAPI, uvicorn | 8001 |

Each template includes `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `.env.example`, and a template `README.md` with run instructions. Generated projects keep that README as a starting point — update it with what your API actually does.

### Base endpoints (no modules)

**`async_io_api`**

- `GET /health`
- `GET /sleep` — async demo endpoint (sleeps 10s)

**`celery_job_api`**

- `GET /health`, `GET /health/ready` (Redis readiness)
- `POST /submit-job` → `job_id`
- `GET /job-status/{job_id}`
- `GET /job-results/{job_id}`

**`webhook_receiver`**

- `POST /webhook` — accepts JSON, passes to engine

## Modules

Modules are optional building blocks applied on top of a template. Pass **public bundle** names to `--modules`; the generator resolves internal dependencies automatically.

| Module | Compatible templates | What it adds |
|---|---|---|
| `identity_auth` | `async_io_api`, `celery_job_api` | Postgres, Alembic, API-key auth (`X-API-Key`), identity-protected routes |
| `usage_metering_auth` | `async_io_api`, `celery_job_api` | Everything in `identity_auth` + usage event recording for metered endpoints |
| `credit_billing_auth` | `async_io_api`, `celery_job_api` | Everything in `usage_metering_auth` + credit balances and per-request billing |
| `webhook_sender` | `celery_job_api` | Submit jobs with a callback URL; Celery delivers results via HTTP POST |

`identity_auth`, `usage_metering_auth`, and `credit_billing_auth` are bundles — they pull in lower-level modules (`api_key_identity_core`, endpoint integrations, DB schema, etc.) in the correct order. You only need to name the bundle.

DB-backed modules add a `db` Postgres service and a `migrate` one-shot container to `docker-compose.yml`. Run `docker compose up --build` and migrations apply automatically.

### Endpoints added by modules

**`identity_auth`**

| Template | Routes |
|---|---|
| `async_io_api` | `GET /protected/me` |
| `celery_job_api` | `POST /identity/submit-job`, `GET /identity/job-status/{job_id}`, `GET /identity/job-results/{job_id}` |

**`usage_metering_auth`** (includes `identity_auth`)

| Template | Routes |
|---|---|
| `async_io_api` | `GET /metered/sleep` |
| `celery_job_api` | `POST /metered/submit-job`, `GET /metered/job-status/{job_id}`, `GET /metered/job-results/{job_id}` |

**`credit_billing_auth`** (includes `usage_metering_auth`)

| Template | Routes |
|---|---|
| `async_io_api` | `GET /billed/sleep` (returns 402 if insufficient credits) |
| `celery_job_api` | `POST /billed/submit-job`, `GET /billed/job-status/{job_id}`, `GET /billed/job-results/{job_id}` |

**`webhook_sender`**

- `POST /submit-job-with-webhook` — body includes `webhook_url`; result is POSTed to that URL when the job completes

Module manifests live under `modules/<name>/manifest.yml` for full details (env vars, copied files, patches).

## Recipes

Common combinations:

**Minimal async API**

```bash
python scripts/new_project.py --template async_io_api --name my-api --path ./out
```

**Async API with auth**

```bash
python scripts/new_project.py \
  --template async_io_api \
  --name my-api \
  --path ./out \
  --modules identity_auth
```

**Celery job API with auth and outbound webhooks**

```bash
python scripts/new_project.py \
  --template celery_job_api \
  --name my-worker-api \
  --path ./out \
  --modules identity_auth,webhook_sender
```

**Metered Celery API (usage tracking per request)**

```bash
python scripts/new_project.py \
  --template celery_job_api \
  --name my-metered-api \
  --path ./out \
  --modules usage_metering_auth
```

**Inbound webhook handler (standalone)**

```bash
python scripts/new_project.py \
  --template webhook_receiver \
  --name my-webhook-api \
  --path ./out
```

`webhook_receiver` does not support optional modules today.

## After generation

1. `cd` into the new project directory.
2. Follow the template `README.md` — typically `cp .env.example .env` then `docker compose up --build`.
3. Implement your engine (see below).
4. Rewrite the project `README.md` with what your API actually does.

### Where to put your code

| Template | Engine file | What to implement |
|---|---|---|
| `async_io_api` | Add routes under `src/api/routes/` | Your endpoint logic |
| `celery_job_api` | `src/engine/work.py` | `do_work(payload)` — called by the Celery task |
| `webhook_receiver` | `src/engine/processor.py` | `process_webhook(payload)` — called on each `POST /webhook` |

For Celery, the default flow is: route enqueues `run_work` → task calls `do_work` in `engine/work.py`. Replace or extend that function; the routes and job registry stay as scaffolding.

Metered/billed/identity routes are examples of auth-wrapped endpoints — copy their pattern when you add your own protected routes.

### Tests

Each generated project has a minimal pytest setup under `src/tests/`. From the project root:

```bash
pip install -r requirements.txt
cd src && pytest -v
```

Celery and DB-backed projects need their backing services running (Redis, Postgres) — easiest via `docker compose up`.

Add engine tests alongside the existing health/job tests in `src/tests/`.

## Dev API keys

There is no admin UI or HTTP route to create users or issue API keys. For local development, `identity_auth` (and bundles that include it) seed two users via Alembic migration `0002_seed_dev_identity_data`:

| Email | API key (plaintext) |
|---|---|
| `seed@example.com` | `seed-api-key-plaintext` |
| `other@example.com` | `other-user-api-key-plaintext` |

Send the key in the `X-API-Key` header. Keys are hashed with `API_KEY_SALT` from `.env` (default `dev-api-key-salt`).

To add users outside the seed data, insert into `users` and `api_keys` manually (hash keys with the same logic as `src/db/auth.py`) or add your own provisioning script.

## Repo layout

```
fastapi-templates/
├── scripts/
│   ├── new_project.py      # Generator CLI
│   └── module_registry.py  # Module discovery, compatibility, patching
├── templates/              # Base projects copied on generation
│   ├── async_io_api/
│   ├── celery_job_api/
│   └── webhook_receiver/
└── modules/                # Optional building blocks (manifest.yml each)
```

## Generator options

```
python scripts/new_project.py --help

  --template   Template name (required)
  --name       Output directory name (required)
  --path       Parent directory (default: current directory)
  --modules    Comma-separated module names (optional)
```
