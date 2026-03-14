# FastAPI Templates

Catalogue of API templates and building blocks to spin up FastAPI projects quickly.

## TODO

- [x] Sandbox: async I/O API (quick responses, async endpoints)
- [ ] Sandbox: Celery job API (enqueue → job ID → poll or webhook)
- [ ] Extract shared code into `foundation/`, template-specific into `templates/`
- [ ] Implement generator script (`scripts/new_project.py`) + module registry
- [ ] Test generator with async I/O template
- [ ] Add optional modules (rate limit, api_key_auth, idempotency, webhook_sender, job_status_store)

## Usage (later)

```bash
python scripts/new_project.py --template async_io_api --name my-api --path ./out
```
