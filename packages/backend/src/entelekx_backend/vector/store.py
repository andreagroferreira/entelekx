"""Backend-agnostic vector store abstraction."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text


@dataclass
class VectorSearchResult:
    """Single result from a vector search."""

    id: str
    score: float
    metadata: dict[str, Any]
    text: str | None


class VectorStore(ABC):
    """Backend-agnostic vector store interface."""

    @abstractmethod
    async def initialize(self) -> None:
        """Create any required tables or extensions."""

    @abstractmethod
    async def upsert(
        self,
        collection: str,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        """Store or update vectors and their metadata."""

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_embedding: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
        min_score: float | None = None,
    ) -> list[VectorSearchResult]:
        """Return the most similar vectors to the query embedding."""

    @abstractmethod
    async def delete(self, collection: str, ids: list[str]) -> None:
        """Remove vectors by id."""

    @abstractmethod
    async def collections(self) -> list[str]:
        """Return the names of existing collections."""

    def _validate_inputs(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> int:
        """Validate upsert inputs and return the expected dimension."""
        if not ids:
            return 0
        n = len(ids)
        if len(texts) != n or len(embeddings) != n or len(metadata) != n:
            raise ValueError("ids, texts, embeddings and metadata must have the same length")
        dim = len(embeddings[0])
        for emb in embeddings:
            if len(emb) != dim:
                raise ValueError("All embeddings must have the same dimension")
        return dim


class SqliteVecStore(VectorStore):
    """sqlite-vec implementation using one virtual table per collection."""

    def __init__(
        self,
        engine: Any | None = None,
        dimension: int = 384,
        url: str | None = None,
    ):
        self._engine = engine
        self._dimension = dimension
        self._collections: set[str] = set()
        self._url = url or ""

    async def initialize(self) -> None:
        await self._ensure_engine()
        await self._ensure_extension()
        await self._load_collections()

    async def _ensure_engine(self) -> None:
        """Create a dedicated async engine if none was supplied."""
        if self._engine is None:
            from sqlalchemy.ext.asyncio import create_async_engine

            self._engine = create_async_engine(self._url, echo=False, future=True)

    async def _ensure_extension(self) -> None:
        """Load sqlite-vec into the engine connection pool.

        sqlite-vec is an extension that must be loaded per raw aiosqlite
        connection.  The load itself is a transactional no-op, so we commit and
        close the underlying aiosqlite connection to avoid SQLAlchemy pool reset
        attempting a rollback on an already closed sqlite3 connection.
        """
        import sqlite_vec

        async with self._engine.connect() as conn:
            db = await self._raw_db(conn)
            await db.enable_load_extension(True)
            await db.load_extension(sqlite_vec.loadable_path())
            await db.commit()
            await db.close()

    async def _load_collections(self) -> None:
        async with self._engine.connect() as conn:
            db = await self._raw_db(conn)
            cur = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'vec_%'"
            )
            rows = await cur.fetchall()
            await cur.close()
            await db.close()
            self._collections = {row[0] for row in rows}

    @staticmethod
    async def _raw_db(conn: Any) -> Any:
        """Return the underlying aiosqlite connection."""
        return (await conn.get_raw_connection()).driver_connection

    def _vec_table(self, collection: str) -> str:
        return f"vec_{collection}"

    def _text_table(self, collection: str) -> str:
        return f"vec_{collection}_text"

    async def _ensure_collection(self, collection: str, metadata_columns: dict[str, str]) -> None:
        if collection in self._collections:
            return
        vec_table = self._vec_table(collection)
        text_table = self._text_table(collection)
        columns_sql = ", ".join(f"{name} {dtype}" for name, dtype in metadata_columns.items())
        vec_schema = f"embedding float[{self._dimension}]"
        if columns_sql:
            vec_schema += f", {columns_sql}"
        async with self._engine.connect() as conn:
            db = await self._raw_db(conn)
            await db.enable_load_extension(True)
            import sqlite_vec

            await db.load_extension(sqlite_vec.loadable_path())
            await db.execute(
                f"CREATE TABLE IF NOT EXISTS {text_table} (rowid INTEGER PRIMARY KEY, text TEXT)"
            )
            await db.execute(
                f"CREATE VIRTUAL TABLE IF NOT EXISTS {vec_table} USING vec0({vec_schema})"
            )
            await db.commit()
            await db.close()
        self._collections.add(collection)

    async def upsert(
        self,
        collection: str,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        dim = self._validate_inputs(ids, texts, embeddings, metadata)
        if not ids:
            return
        if dim != self._dimension:
            raise ValueError(
                f"Embedding dimension mismatch for collection '{collection}': "
                f"expected {self._dimension}, got {dim}"
            )

        # Discover metadata columns from first metadata dict.
        meta_columns = self._metadata_columns(metadata)
        await self._ensure_collection(collection, meta_columns)
        vec_table = self._vec_table(collection)
        text_table = self._text_table(collection)

        async with self._engine.connect() as conn:
            db = await self._raw_db(conn)
            await db.enable_load_extension(True)
            import sqlite_vec

            await db.load_extension(sqlite_vec.loadable_path())
            for id_, text_, embedding, meta in zip(ids, texts, embeddings, metadata, strict=True):
                rowid = abs(hash(id_)) % (2**31)
                await db.execute(
                    f"INSERT OR REPLACE INTO {text_table} (rowid, text) VALUES (?, ?)",
                    (rowid, text_),
                )
                emb_json = json.dumps(embedding)
                column_names = ["rowid", "embedding"] + list(meta_columns.keys())
                values = [rowid, emb_json] + [meta.get(col) for col in meta_columns]
                placeholders = ", ".join("?" for _ in values)
                await db.execute(
                    f"INSERT OR REPLACE INTO {vec_table} ({', '.join(column_names)}) "
                    f"VALUES ({placeholders})",
                    values,
                )
            await db.commit()
            await db.close()

    async def search(
        self,
        collection: str,
        query_embedding: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
        min_score: float | None = None,
    ) -> list[VectorSearchResult]:
        if collection not in self._collections:
            return []
        vec_table = self._vec_table(collection)
        text_table = self._text_table(collection)

        where_clauses, params = self._build_filters(filters)
        query_json = json.dumps(query_embedding)
        params.append(query_json)
        limit = max(1, top_k * 3)

        match_clause = "v.embedding MATCH ?"
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses) + f" AND {match_clause}"
        else:
            where_sql = f"WHERE {match_clause}"

        # sqlite-vec requires either a `LIMIT` or `k = ?` constraint; use a
        # parameterised `k` so the query plan is stable and no SQL injection is
        # possible.
        sql = (
            f"SELECT v.rowid, v.distance, t.text FROM {vec_table} v "
            f"JOIN {text_table} t ON v.rowid = t.rowid "
            f"{where_sql} "
            f"AND k = ? "
            f"ORDER BY v.distance"
        )
        params.append(limit)

        async with self._engine.connect() as conn:
            db = await self._raw_db(conn)
            await db.enable_load_extension(True)
            import sqlite_vec

            await db.load_extension(sqlite_vec.loadable_path())
            cur = await db.execute(sql, params)
            rows = await cur.fetchall()
            await cur.close()
            await db.close()

        results: list[VectorSearchResult] = []
        for row in rows:
            rowid, distance, text_ = row
            score = 1.0 - float(distance)
            if min_score is not None and score < min_score:
                continue
            results.append(
                VectorSearchResult(
                    id=str(rowid),
                    score=score,
                    metadata={"rowid": rowid},
                    text=text_,
                )
            )
        return results[:top_k]

    async def delete(self, collection: str, ids: list[str]) -> None:
        if collection not in self._collections or not ids:
            return
        vec_table = self._vec_table(collection)
        text_table = self._text_table(collection)
        rowids = [abs(hash(id_)) % (2**31) for id_ in ids]
        placeholders = ", ".join("?" for _ in rowids)
        async with self._engine.connect() as conn:
            db = await self._raw_db(conn)
            await db.enable_load_extension(True)
            import sqlite_vec

            await db.load_extension(sqlite_vec.loadable_path())
            await db.execute(f"DELETE FROM {vec_table} WHERE rowid IN ({placeholders})", rowids)
            await db.execute(f"DELETE FROM {text_table} WHERE rowid IN ({placeholders})", rowids)
            await db.commit()
            await db.close()

    async def collections(self) -> list[str]:
        await self._load_collections()
        return sorted(self._collections)

    @staticmethod
    def _metadata_columns(metadata: list[dict[str, Any]]) -> dict[str, str]:
        """Return column name -> SQLite type for metadata used in the virtual table."""
        columns: dict[str, str] = {}
        for meta in metadata:
            for key, value in meta.items():
                if key in columns:
                    continue
                if isinstance(value, bool | int):
                    columns[key] = "INTEGER"
                elif isinstance(value, float):
                    columns[key] = "REAL"
                else:
                    columns[key] = "TEXT"
        return columns

    @staticmethod
    def _build_filters(filters: dict[str, Any] | None) -> tuple[list[str], list[Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if not filters:
            return clauses, params
        for key, value in filters.items():
            clauses.append(f"v.{key} = ?")
            params.append(value)
        return clauses, params


class PgVectorStore(VectorStore):
    """pgvector implementation (Phase 0 focus: interface + stub)."""

    def __init__(self, engine: Any | None = None, dimension: int = 384):
        self._engine = engine
        self._dimension = dimension
        self._collections: set[str] = set()

    async def initialize(self) -> None:
        if self._engine is None:
            return
        async with self._engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name LIKE 'vec_%'"
                )
            )
            rows = result.fetchall()
            self._collections = {row[0] for row in rows}

    def _vec_table(self, collection: str) -> str:
        return f"vec_{collection}"

    async def _ensure_collection(self, collection: str) -> None:
        if collection in self._collections:
            return
        table = self._vec_table(collection)
        async with self._engine.begin() as conn:
            await conn.execute(
                text(
                    f"CREATE TABLE IF NOT EXISTS {table} ("
                    "id TEXT PRIMARY KEY, "
                    "text TEXT, "
                    "embedding vector(:dim), "
                    "metadata JSONB DEFAULT '{}', "
                    "created_at TIMESTAMP DEFAULT NOW()"
                    ")"
                ),
                {"dim": self._dimension},
            )
            await conn.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS idx_{table}_embedding ON {table} USING ivfflat (embedding vector_cosine_ops)"
                )
            )
        self._collections.add(collection)

    async def upsert(
        self,
        collection: str,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        dim = self._validate_inputs(ids, texts, embeddings, metadata)
        if not ids:
            return
        if dim != self._dimension:
            raise ValueError(
                f"Embedding dimension mismatch for collection '{collection}': "
                f"expected {self._dimension}, got {dim}"
            )
        await self._ensure_collection(collection)
        table = self._vec_table(collection)
        async with self._engine.begin() as conn:
            for id_, text_, embedding, meta in zip(ids, texts, embeddings, metadata, strict=True):
                await conn.execute(
                    text(
                        f"INSERT INTO {table} (id, text, embedding, metadata) "
                        "VALUES (:id, :text, :embedding::vector, :metadata::jsonb) "
                        "ON CONFLICT (id) DO UPDATE SET "
                        "text = EXCLUDED.text, "
                        "embedding = EXCLUDED.embedding, "
                        "metadata = EXCLUDED.metadata"
                    ),
                    {
                        "id": id_,
                        "text": text_,
                        "embedding": str(embedding),
                        "metadata": json.dumps(meta),
                    },
                )

    async def search(
        self,
        collection: str,
        query_embedding: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
        min_score: float | None = None,
    ) -> list[VectorSearchResult]:
        if collection not in self._collections:
            return []
        table = self._vec_table(collection)
        limit = max(1, top_k * 3)
        where_sql = ""
        params: dict[str, Any] = {"query": str(query_embedding), "limit": limit}
        if filters:
            clauses = []
            for idx, (_key, value) in enumerate(filters.items()):
                param = f"filter_{idx}"
                clauses.append(f"metadata->>{':{param}'} = :{param}")
                params[param] = str(value)
            where_sql = "WHERE " + " AND ".join(clauses)
        sql = (
            f"SELECT id, text, metadata, "
            f"1 - (embedding <=> :query::vector) AS score "
            f"FROM {table} {where_sql} "
            f"ORDER BY embedding <=> :query::vector LIMIT :limit"
        )
        async with self._engine.connect() as conn:
            result = await conn.execute(text(sql), params)
            rows = result.fetchall()
        results: list[VectorSearchResult] = []
        for row in rows:
            id_, text_, meta, score = row
            if min_score is not None and score < min_score:
                continue
            results.append(VectorSearchResult(id=id_, score=score, metadata=meta, text=text_))
        return results[:top_k]

    async def delete(self, collection: str, ids: list[str]) -> None:
        if collection not in self._collections or not ids:
            return
        table = self._vec_table(collection)
        placeholders = ", ".join(f":id_{i}" for i in range(len(ids)))
        params = {f"id_{i}": id_ for i, id_ in enumerate(ids)}
        async with self._engine.begin() as conn:
            await conn.execute(text(f"DELETE FROM {table} WHERE id IN ({placeholders})"), params)

    async def collections(self) -> list[str]:
        return sorted(self._collections)


def get_vector_store(
    database_url: str, engine: Any | None = None, dimension: int = 384
) -> VectorStore:
    if database_url.startswith("postgresql"):
        return PgVectorStore(engine, dimension)
    return SqliteVecStore(engine, dimension, url=database_url)
