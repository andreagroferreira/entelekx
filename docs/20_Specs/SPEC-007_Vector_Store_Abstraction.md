---
type: spec
status: draft
feature: vector-store-abstraction
project: entelekx
date_created: 2026-06-21
tags: [spec, entelekx, vector, rag, foundation]
---

# SPEC-007: Vector Store Abstraction

## Overview

**Problem:** EntelekX relies on embeddings for memory, RAG and adaptive context. The default backend is PostgreSQL + pgvector, but the SQLite fallback requires sqlite-vec. Application logic must not branch between backends.

**Goal:** Provide a backend-agnostic vector store interface with concrete implementations for pgvector, sqlite-vec and a future Qdrant upgrade path.

**Actors:**
- Agent Kernel (stores/retrieves memories).
- Adaptive Context (stores user/project models and preferences).
- RAG pipeline (retrieves relevant documents/messages).
- Developers (add new backends).

## Scope

### In scope

- `VectorStore` abstract interface.
- `PgVectorStore` implementation.
- `SqliteVecStore` implementation.
- Collection management.
- Hybrid search (vector + keyword + metadata filters).
- Embedding dimension normalisation.

### Out of scope

- Advanced re-ranking models in MVP.
- Distributed vector databases in MVP.
- Real-time vector sync across machines.

## Acceptance Criteria

1. **Given** a configured backend, **when** code calls `vector_store.upsert()`, **then** embeddings are stored.
2. **Given** a query embedding, **when** code calls `vector_store.search()`, **then** relevant items are returned with scores.
3. **Given** metadata filters (e.g. `project_id=xyz`), **when** search runs, **then** only matching items are considered.
4. **Given** the same interface, **when** switching from Postgres to SQLite, **then** no application code changes.
5. **Given** a deleted memory, **when** `vector_store.delete()` runs, **then** the vector is removed.

## Data Model

### Conceptual collections

| Collection | Contents | Typical fields |
|---|---|---|
| `memories` | Extracted facts, preferences | project_id, source, created_at |
| `messages` | Chat message summaries | session_id, role, created_at |
| `documents` | Notes and specs | project_id, title, tags |
| `artefacts` | Generated file descriptions | project_id, type, path |
| `decisions` | Decision summaries | project_id, status |

### Result schema

```python
class VectorSearchResult:
    id: str
    score: float
    metadata: dict
    text: str | None
```

## API Contracts

```python
class VectorStore(ABC):
    async def initialize(self) -> None: ...
    async def upsert(
        self,
        collection: str,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadata: list[dict],
    ) -> None: ...
    async def search(
        self,
        collection: str,
        query_embedding: list[float],
        top_k: int = 10,
        filters: dict | None = None,
        min_score: float | None = None,
    ) -> list[VectorSearchResult]: ...
    async def delete(self, collection: str, ids: list[str]) -> None: ...
    async def collections(self) -> list[str]: ...
```

## Hybrid Search Algorithm

1. **Vector search**: retrieve `top_k * 3` candidates by cosine similarity.
2. **Keyword search**: run FTS on the same collection with the same query text.
3. **Merge**: combine candidates, deduplicate, normalise scores.
4. **Metadata filter**: apply filters (project_id, date, type).
5. **Re-rank**: simple weighted score (vector 70%, keyword 30%) in MVP.
6. **Return** top_k results.

## UI/UX Requirements

- None directly; surfaced through chat memory quality.

## Edge Cases

1. **Empty collection:** search returns empty list, no error.
2. **Embedding dimension mismatch:** raise clear error, do not silently truncate.
3. **All vectors deleted:** collection still exists, searches return empty.
4. **Keyword-only query:** fall back to FTS without vector.
5. **Backend missing extension:** fail fast with actionable error.

## Test Scenarios

| # | Scenario | Type | Expected |
|---|---|---|---|
| 1 | Upsert and search on Postgres | Integration | Correct top-k |
| 2 | Upsert and search on SQLite | Integration | Correct top-k |
| 3 | Metadata filter excludes wrong project | Integration | Only project-scoped results |
| 4 | Delete removes vector | Integration | Search no longer returns it |
| 5 | Empty collection search | Unit | Empty list |
| 6 | Hybrid search ranks keyword match higher | Unit | Keyword-relevant item scores better |
| 7 | Embedding dimension mismatch raises | Unit | Clear exception |

## Dependencies

- [ ] SPEC-006 Database Abstraction approved.
- [ ] fastembed or sentence-transformers for embeddings.
- [ ] pgvector test environment.
- [ ] sqlite-vec test environment.

## Open Questions

- Should hybrid search re-ranking use a dedicated cross-encoder later?
- Should collections share embedding dimensions or allow per-collection dimensions?

## Related

- [[SPEC-006_Database_Abstraction]]
- [[10_Architecture/05_Vector_Store_Abstraction]]
- [[30_Decisions/ADR-008_Vector_Store_Abstraction]]
- [[50_Research/sqlite_vec]]
