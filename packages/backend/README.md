# EntelekX Backend

Python FastAPI backend for EntelekX.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run entelekx --help
```

## Run locally

```bash
uv run uvicorn entelekx_backend.main:app --reload --port 7349
```

## Migrations

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```
