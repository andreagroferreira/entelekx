# ADR-008: Vector Store Abstraction

## Status

Approved

## Context

Vector search is needed for memory, RAG and adaptive context. Different users will run different database backends.

## Decision

Implement a swappable vector store abstraction with concrete backends for:
- PostgreSQL + pgvector (default).
- SQLite + sqlite-vec (fallback).
- Qdrant (future upgrade path).

## Consequences

### Positive

- Backend-agnostic application logic.
- Easy to add high-performance vector DB later.
- Full RAG functionality in both default and fallback modes.

### Negative

- Need to maintain multiple backend implementations.
- Hybrid search logic must be tuned per backend.

## Alternatives Considered

- **Use ChromaDB for everyone:** adds another service/process.
- **Skip vector abstraction and use pgvector only:** breaks SQLite fallback promise.

## Related

- [[../10_Architecture/05_Vector_Store_Abstraction]]
- [[SPEC-007_Vector_Store_Abstraction]]
