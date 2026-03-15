# Async I/O API (template)

Quick async endpoints: health check + a dummy `/sleep` that async-sleeps 10s.

**Run (from repo root):**
```bash
cd templates/async_io_api && uvicorn main:app --reload
```
Use a venv with deps from repo root: `pip install -r ../../requirements.txt`.

**Test:**
```bash
# from repo root (venv active)
cd templates/async_io_api && pytest -v
```

**Endpoints:** `GET /health`, `GET /sleep` (10s).
