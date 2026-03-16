# Celery Job API (template)

Submit work as jobs; get a job ID, check status, and fetch the result. Uses Celery + Redis.

## Run with Docker (recommended)

From the generated project directory (this template copied there):

```bash
cp .env.example .env
docker compose up --build
```

Services:

- `redis` on port `6379`
- `api` on port `8000`
- `worker` running the Celery worker

The API will be available at `http://localhost:8000`.

## Local development (without Docker)

From the project root, with a virtualenv active:

```bash
pip install -r requirements.txt
cp .env.example .env
cd src
uvicorn main:app --reload
```

Run a Celery worker in a separate terminal (with Redis running, e.g. via Docker or locally):

```bash
cd src
celery -A core.celery_app worker -l info
```

## Tests

From the project root (venv active):

```bash
cd src
pytest -v
```

Requires Redis running (lifespan pings Redis on startup).

## Endpoints

- `POST /submit-job` → enqueue work, returns `job_id`
- `GET /job-status/{job_id}` → job status (404 if unknown id)
- `GET /job-results/{job_id}` → job result when ready (202 while pending, 404 if unknown id)
