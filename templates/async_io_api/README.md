# Async I/O API (template)

Quick async endpoints: health check + a dummy `/sleep` that async-sleeps 10s.

## Run with Docker (recommended)

From the generated project directory (this template copied there):

```bash
cp .env.example .env   # optional
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Local development (without Docker)

From the project root, with a virtualenv active:

```bash
pip install -r requirements.txt
cd src
uvicorn main:app --reload
```

## Tests

From the project root (venv active):

```bash
cd src
pytest -v
```

## Endpoints

- `GET /health`
- `GET /sleep` (sleeps 10 seconds)
