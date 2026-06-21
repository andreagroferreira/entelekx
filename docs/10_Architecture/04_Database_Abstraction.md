# EntelekX — Database Abstraction

## Goal

EntelekX must work with PostgreSQL + pgvector by default, but degrade gracefully to SQLite + sqlite-vec when the user cannot or will not run Postgres. The application code must not care which backend is active.

## Interface Design

```python
# Abstract session factory
class DatabaseBackend(ABC):
    async def connect(self): ...
    async def disconnect(self): ...
    def get_session(self) -> AsyncSession: ...

# Detection
async def detect_or_setup_database(config: DatabaseConfig) -> DatabaseBackend:
    if config.url.startswith("postgresql"):
        return PostgresBackend(config)
    if config.url.startswith("sqlite"):
        return SQLiteBackend(config)
    raise UnsupportedDatabaseError(...)
```

## Responsibilities per Backend

| Task | Postgres | SQLite |
|---|---|---|
| Connection pool | asyncpg | aiosqlite |
| Migrations | Alembic with custom env | Alembic with custom env |
| Vector extension | pgvector | sqlite-vec |
| Full-text search | pg_trgm + tsvector | FTS5 |
| JSON metadata | JSONB | JSONB-compatible via TEXT/JSON |
| Concurrency | Excellent | Good enough for single user |

## Migration Strategy

- Use Alembic for both backends.
- Keep migrations backend-aware via `if backend == 'postgresql'` checks.
- Avoid raw SQL where possible; rely on SQLModel/SQLAlchemy abstractions.
- Provide a single command: `entelekx db migrate`.

## Connection String Resolution

1. If `DATABASE_URL` is set in `.env`, use it.
2. If Postgres.app is detected, create/configure a local DB.
3. If Homebrew Postgres is detected, use it.
4. If managed Postgres is provided, test and use.
5. Otherwise fall back to `sqlite:///~/.entelekx/data/app.db`.

## Testing

- Run the full test suite against both backends in CI.
- Use `pytest` markers `@pytest.mark.postgres` and `@pytest.mark.sqlite`.

## Related

- [[03_Data_Architecture]]
- [[05_Vector_Store_Abstraction]]
- [[20_Specs/SPEC-006_Database_Abstraction]]
- [[30_Decisions/ADR-002_Data_Platform_Postgres_pgvector_sqlite_vec]]
- [[30_Decisions/ADR-005_Smart_Database_Selector]]
