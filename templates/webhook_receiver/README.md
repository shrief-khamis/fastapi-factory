# Webhook Receiver API (template)

Simple FastAPI service that exposes a single `/webhook` endpoint to receive POST callbacks and hand them off to an engine for processing.
For now, the engine just logs the received payload; you can replace it with your own logic.

## Run with Docker (recommended)

From the generated project directory (this template copied there):

```bash
cp .env.example .env   # optional
docker compose up --build
```

The API will be available at `http://localhost:8001`.

## Local development (without Docker)

From the project root, with a virtualenv active:

```bash
pip install -r requirements.txt
cp .env.example .env  # optional
cd src
uvicorn main:app --reload --port 8001
```

## Tests

From the project root (venv active):

```bash
cd src
pytest -v
```

## Endpoint

- `POST /webhook` – accepts a JSON payload and passes it to the engine for processing.

