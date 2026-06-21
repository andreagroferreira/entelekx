# EntelekX — Vector Store Abstraction

## Goal

Vector search (embeddings) is critical for memory, RAG and adaptive context. EntelekX must support multiple vector backends without changing application logic.

## Supported Backends

| Backend | Default for | Notes |
|---|---|---|
| **pgvector** | PostgreSQL | Native vectors, similarity operators, metadata filtering in one query |
| **sqlite-vec** | SQLite | In-process vectors for fallback mode |
| **Qdrant** | Future upgrade | High-performance dedicated vector DB |

## Abstract Interface

```python
class VectorStore(ABC):
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
        min_distance: float | None = None,
    ) -> list[VectorSearchResult]: ...

    async def delete(self, collection: str, ids: list[str]) -> None: ...

    async def collections(self) -> list[str]: ...
```

## Collections

| Collection | Contents |
|---|---|
| `memories` | Stored facts, insights, preferences |
| `messages` | Chat messages (with decay/retention policy) |
| `documents` | Notes, specs, design files |
| `artefacts` | Generated files and media descriptions |
| `decisions` | Decision logs and outcomes |

## Hybrid Search

For each query, EntelekX combines:
1. **Vector similarity** (semantic meaning).
2. **Keyword search** (exact matches, names, IDs).
3. **Metadata filtering** (project_id, date range, source).

Result scores are normalised and re-ranked.

## Embedding Models

Default: fastembed small models (e.g. `BAAI/bge-small-en-v1.5`, 384-dim).  
Upgrade path: `sentence-transformers`, OpenAI, Voyage, Cohere via provider settings.

## Related

- [[03_Data_Architecture]]
- [[04_Database_Abstraction]]
- [[20_Specs/SPEC-007_Vector_Store_Abstraction]]
- [[30_Decisions/ADR-008_Vector_Store_Abstraction]]
- [[50_Research/sqlite_vec]]
