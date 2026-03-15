# Celery Job API (template)

Submit work as jobs; get a job ID, check status, and fetch the result. Uses Celery + Redis.

## Install on your machine (no Docker)

- **Redis:**  
  - macOS: `brew install redis` then `brew services start redis`  
  - Linux (Debian/Ubuntu): `sudo apt install redis-server` then `sudo systemctl start redis-server`  
  - Check: `redis-cli ping` → `PONG`
- **Celery:** No system install. Use the same Python venv as the API; `pip install -r requirements.txt` (or from repo root) installs `celery` and `redis`.

## Run

1. **Start Redis** (if not already running), e.g. `brew services start redis` or `redis-server`.

2. **Install deps** (from repo root with venv active):
   ```bash
   pip install -r templates/celery_job_api/requirements.txt
   ```
   Or use the global repo `requirements.txt` if it includes celery/redis.

3. **Copy env and run API:**
   ```bash
   cd templates/celery_job_api
   cp .env.example .env
   uvicorn main:app --reload
   ```
   The API will exit on startup if Redis is not reachable.

4. **Run a Celery worker** (separate terminal, same venv and cwd):
   ```bash
   cd templates/celery_job_api
   celery -A core.celery_app worker -l info
   ```

5. **Test:**  
   - `POST /submit-job` with body `{"data": "hello"}` → returns `job_id`.  
   - `GET /job-status/<id>` → status (404 if unknown id).  
   - `GET /job-results/<id>` → result when ready (202 while pending, 404 if unknown id).

## Tests

From `templates/celery_job_api` (venv active):

```bash
pytest -v
```

Requires Redis running (lifespan pings Redis on startup).
