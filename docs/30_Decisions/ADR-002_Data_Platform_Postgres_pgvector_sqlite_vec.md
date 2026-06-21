# ADR-002: Data Platform — PostgreSQL + pgvector with SQLite + sqlite-vec Fallback

## Status

Approved

## Context

EntelekX needs a database that supports structured data, embeddings, full-text search and rich metadata. SQLite is common for self-hosted apps but limits future AI capabilities.

## Decision

- **Default:** PostgreSQL 16+ with pgvector extension.
- **Fallback:** SQLite with sqlite-vec extension.
- The application uses a database abstraction layer to work transparently with both.

## Consequences

### Positive

- Postgres gives ACID, JSONB, vectors, FTS and mature tooling from day one.
- sqlite-vec allows full RAG functionality even without Postgres.
- Users can start on SQLite and upgrade to Postgres later.
- One ORM (SQLModel) and one migration tool (Alembic) for both.

### Negative

- Need to maintain backend-aware migrations.
- sqlite-vec is newer and less battle-tested than pgvector.

## Alternatives Considered

- **SQLite default with ChromaDB for vectors:** two systems, harder backups.
- **Postgres default without fallback:** excludes users who cannot run Postgres easily.

## Related

- [[../10_Architecture/03_Data_Architecture]]
- [[../10_Architecture/04_Database_Abstraction]]
- [[../10_Architecture/05_Vector_Store_Abstraction]]
- [[SPEC-006_Database_Abstraction]]
