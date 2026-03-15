# FastAPI Templates

Catalogue of API templates and building blocks to spin up FastAPI projects quickly.

## TODO

- [x] Template: async I/O API (quick responses, async endpoints)
- [x] Template: Celery job API (enqueue → job ID → poll or webhook)
- [ ] Create generator script; copy template to target path and rename
- [ ] Test generator on base templates (async_io_api, celery_job_api)
- [ ] Add modules patcher + wire generator to run chosen modules on generated project
- [ ] Optional modules (rate limit, api_key_auth, idempotency, webhook_sender, job_status_store)

## Usage (later)

```bash
python scripts/new_project.py --template async_io_api --name my-api --path ./out
```
