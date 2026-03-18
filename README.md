# FastAPI Templates

Catalogue of API templates and building blocks to spin up FastAPI projects quickly.

## TODO

- [x] Template: async I/O API (quick responses, async endpoints)
- [x] Template: Celery job API (enqueue → job ID → poll or webhook)
- [x] Create generator script; copy template to target path and rename
- [x] Test generator on base templates (async_io_api, celery_job_api)
- [x] Add Dockerfile and docker-compose for templates; move code under src/
- [x] Add a webhook receiver template
- [x] Add modules patcher + wire generator to run chosen modules on generated project
- [x] Add first optional module, webhook sender

## Usage (later)

```bash
python scripts/new_project.py --template async_io_api --name my-api --path ./out
```
