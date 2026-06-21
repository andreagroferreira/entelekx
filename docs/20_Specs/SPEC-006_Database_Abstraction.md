---
type: spec
status: draft
feature: database-abstraction
project: entelekx
date_created: 2026-06-21
tags: [spec, entelekx, database, foundation]
---

# SPEC-006: Database Abstraction

## Overview

**Problem:** EntelekX targets non-technical founders and developers who want a two-minute setup. PostgreSQL + pgvector is the ideal default, but many users will not have it. We must support SQLite + sqlite-vec as a functional fallback without two codebases.

**Goal:** Provide a single application-level database abstraction that works transparently across PostgreSQL + pgvector and SQLite + sqlite-vec, using one ORM and one migration path.

**Actors:**
- End user (installs EntelekX).
- Setup wizard (detects/configures DB).
- Backend code (queries, migrations, vector operations).
- CI (tests both backends).

## Scope

### In scope

- SQLModel/SQLAlchemy 2 ORM models.
- Async database backend abstraction (`PostgresBackend`, `SQLiteBackend`).
- Alembic migrations compatible with both backends.
- Connection string detection and validation.
- Health checks.
- Automatic creation of DB, user and pgvector extension when using local Postgres.
- SQLite fallback with sqlite-vec for vectors.

### Out of scope

- Multi-tenant row-level security (future).
- Database replication / clustering.
- Support for MySQL or other databases in MVP.
- Cloud-native managed backup service.

## Acceptance Criteria

1. **Given** a `DATABASE_URL=postgresql://...`, **when** the backend starts, **then** it connects, runs migrations, enables pgvector and serves requests.
2. **Given** no Postgres and user declines install, **when** the wizard finishes, **then** SQLite + sqlite-vec is configured and functional.
3. **Given** either backend, **when** application code calls `get_session()`, **then** it receives a working async session without knowing the backend.
4. **Given** a schema change, **when** Alembic runs, **then** it applies correctly on both Postgres and SQLite.
5. **Given** SQLite mode, **when** vector search runs, **then** sqlite-vec returns relevant results without error.
6. **Given** Postgres mode, **when** vector search runs, **then** pgvector returns relevant results.

## Data Model

### Core tables (both backends)

| Entity | Purpose | Key fields |
|---|---|---|
| `users` | Single operator (future multi-user) | id, username, password_hash, created_at |
| `projects` | Scope most data | id, user_id, name, slug, description, settings |
| `sessions` | Chat threads | id, project_id, title, model, created_at, updated_at |
| `messages` | Chat messages | id, session_id, role, content, metadata, created_at |
| `tool_calls` | Tool invocations | id, message_id, name, arguments, result, status |
| `memories` | Extracted facts | id, project_id, content, source, created_at |
| `documents` | Notes/specs | id, project_id, title, body, tags, created_at, updated_at |
| `decisions` | Decision log | id, project_id, question, options, reasoning, outcome |
| `goals` | Targets | id, project_id, title, status, progress, parent_id |
| `tasks` | Todos | id, project_id, title, status, due_date, goal_id |
| `events` | Calendar entries | id, project_id, title, start_time, end_time, recurrence |
| `artefacts` | Generated files/media | id, project_id, type, path, metadata, created_at |
| `provider_configs` | API keys per provider | id, provider, encrypted_key, settings |
| `backups` | Backup job metadata | id, path, size, status, created_at |

### Vector storage

| Backend | Mechanism |
|---|---|
| PostgreSQL | `pgvector` extension; embeddings stored in `vector(384)` columns or separate table |
| SQLite | `sqlite-vec` virtual tables |

## API Contracts

### Internal (not exposed to UI)

```python
class DatabaseBackend(ABC):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    def get_session(self) -> AsyncSession: ...
    async def health_check(self) -> bool: ...
    async def create_database_if_not_exists(self) -> None: ...
    async def enable_vector_extension(self) -> None: ...
```

### HTTP

- `GET /api/health/db` — returns backend type and connectivity status.

## UI/UX Requirements

- Setup wizard database step (see SPEC-005).
- Settings page shows active backend and connection status.
- Warning banner if running SQLite fallback.

## Edge Cases

1. **Port 5432 busy:** if local Postgres cannot bind, fail gracefully and offer managed/SQLite.
2. **pgvector not installed:** detect and attempt `CREATE EXTENSION IF NOT EXISTS vector`; if fails, guide user.
3. **SQLite DB locked:** implement retry with exponential backoff.
4. **Migration conflict:** if Alembic head mismatch, prompt user to backup and reset or manual fix.
5. **Managed Postgres without pgvector:** warn and disable vector features, or fallback to sqlite-vec for vectors.

## Test Scenarios

| # | Scenario | Type | Expected |
|---|---|---|---|
| 1 | Backend auto-detects Postgres URL | Unit | Returns PostgresBackend |
| 2 | Backend auto-detects SQLite URL | Unit | Returns SQLiteBackend |
| 3 | Migrations run on clean Postgres | Integration | All tables created, pgvector enabled |
| 4 | Migrations run on clean SQLite | Integration | All tables created, sqlite-vec enabled |
| 5 | Create project + session on both backends | Integration | Data persisted and retrievable |
| 6 | Vector upsert/search on Postgres | Integration | Correct top-k results |
| 7 | Vector upsert/search on SQLite | Integration | Correct top-k results |
| 8 | Health check returns true when DB healthy | Unit | True |
| 9 | Health check returns false when DB unreachable | Unit | False |

## Dependencies

- [ ] SQLModel + SQLAlchemy 2 configured.
- [ ] Alembic setup.
- [ ] asyncpg and aiosqlite installed.
- [ ] pgvector available in Postgres test image.
- [ ] sqlite-vec available in Python test environment.

## Open Questions

- Should vector dimensions be configurable per embedding model?
- How do we handle migration from SQLite to Postgres later?

## Related

- [[SPEC-005_Installation_Wizard]]
- [[SPEC-007_Vector_Store_Abstraction]]
- [[10_Architecture/03_Data_Architecture]]
- [[10_Architecture/04_Database_Abstraction]]
- [[30_Decisions/ADR-002_Data_Platform_Postgres_pgvector_sqlite_vec]]
