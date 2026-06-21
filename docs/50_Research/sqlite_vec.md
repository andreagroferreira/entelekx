# sqlite-vec

## Summary

`sqlite-vec` is an extension for SQLite that adds vector search capabilities. It allows EntelekX to provide full RAG and memory functionality even when PostgreSQL + pgvector is not available.

## Why It Matters

- EntelekX promises no degradation of RAG in fallback mode.
- sqlite-vec is zero-config and works in-process.
- It avoids adding a separate vector service (like ChromaDB) just for SQLite users.

## Features

- Store and query float vectors in SQLite.
- Similarity search with distance functions.
- Metadata columns alongside vectors.
- Works with aiosqlite for async access.

## Usage Pattern

```sql
CREATE VIRTUAL TABLE vec_memories USING vec0(
    id TEXT PRIMARY KEY,
    embedding FLOAT[384],
    project_id TEXT,
    content TEXT
);

SELECT id, distance
FROM vec_memories
WHERE project_id = 'proj_123'
ORDER BY embedding MATCH ?
LIMIT 10;
```

## Integration in EntelekX

- `SqliteVecStore` implements the shared `VectorStore` interface.
- Collections map to separate virtual tables.
- Hybrid search combines vector + FTS5.

## Trade-offs

- Less mature than pgvector.
- Lower concurrency than Postgres.
- Sufficient for personal single-user workloads.

## Related

- [[../10_Architecture/04_Database_Abstraction]]
- [[../10_Architecture/05_Vector_Store_Abstraction]]
- [[../20_Specs/SPEC-006_Database_Abstraction]]
- [[../20_Specs/SPEC-007_Vector_Store_Abstraction]]
