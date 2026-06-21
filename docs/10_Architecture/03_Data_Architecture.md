# EntelekX — Data Architecture

## Principles

1. **Single source of truth:** PostgreSQL is the default; SQLite is a degraded but functional fallback.
2. **AI-native schema:** design for embeddings, vectors, JSONB metadata, graph-like relations and full-text search.
3. **Project-centric:** most entities belong to a project; the user can have many projects.
4. **Event-sourced history:** important changes are logged immutably.
5. **Privacy by design:** sensitive data is encrypted at rest when necessary.
6. **Migration-ready:** Alembic from day one.

## Logical Entities

| Entity | Purpose |
|---|---|
| `User` | The single operator (single-user by default; multi-user optional future) |
| `Project` | A software project, business initiative or life domain |
| `Session` | A conversation thread |
| `Message` | A chat message (user, assistant, tool, system) |
| `ToolCall` | A recorded tool invocation and its result |
| `Memory` | A stored fact, insight or preference |
| `Embedding` | Vector representation of a memory/message/document |
| `Document` | A note, spec, design file or artefact |
| `Decision` | A recorded decision with reasoning and outcome |
| `Goal` | A target with milestones |
| `Task` | A todo or scheduled item |
| `Event` | Calendar / timeline entry |
| `ProviderConfig` | API keys and settings per model provider |
| `ModelEndpoint` | Custom endpoint definitions |
| `Skill` | Reusable skill definitions |
| `Artefact` | Generated file or media object |
| `Backup` | Backup job metadata |

## Key Relations

```
User
 └── Project
      ├── Session
      │    └── Message
      │         └── ToolCall
      ├── Memory
      │    └── Embedding
      ├── Document
      ├── Decision
      ├── Goal
      ├── Task
      ├── Event
      └── Artefact
```

## PostgreSQL + pgvector Schema Highlights

- Use `uuid` primary keys.
- Use `project_id` as the main scoping column.
- Store embeddings in `vector(384)` or `vector(768)` columns (depending on embedding model).
- Use `pg_trgm` for keyword search.
- Use JSONB for flexible metadata.
- Partition large event tables by time if needed.

## SQLite + sqlite-vec Fallback

- Same logical schema via SQLModel.
- Embeddings stored via sqlite-vec virtual tables.
- Full-text via FTS5.
- Reduced concurrency but sufficient for single-user personal use.

## Encryption

- Provider API keys and sensitive tokens encrypted with Fernet.
- Encryption key derived from machine fingerprint + user password salt.
- Backup archives encrypted optionally.

## Related

- [[04_Database_Abstraction]]
- [[05_Vector_Store_Abstraction]]
- [[30_Decisions/ADR-002_Data_Platform_Postgres_pgvector_sqlite_vec]]
- [[30_Decisions/ADR-008_Vector_Store_Abstraction]]
