"""Vector store abstraction stubs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class VectorSearchResult:
    id: str
    score: float
    metadata: dict[str, Any]
    text: str | None


class VectorStore(ABC):
    """Backend-agnostic vector store interface."""

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def upsert(
        self,
        collection: str,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None: ...

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_embedding: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
        min_score: float | None = None,
    ) -> list[VectorSearchResult]: ...

    @abstractmethod
    async def delete(self, collection: str, ids: list[str]) -> None: ...

    @abstractmethod
    async def collections(self) -> list[str]: ...


class PgVectorStore(VectorStore):
    """pgvector implementation (stub for Phase 0)."""

    async def initialize(self) -> None:
        pass

    async def upsert(self, collection, ids, texts, embeddings, metadata):
        pass

    async def search(self, collection, query_embedding, top_k=10, filters=None, min_score=None):
        return []

    async def delete(self, collection, ids):
        pass

    async def collections(self):
        return []


class SqliteVecStore(VectorStore):
    """sqlite-vec implementation (stub for Phase 0)."""

    async def initialize(self) -> None:
        pass

    async def upsert(self, collection, ids, texts, embeddings, metadata):
        pass

    async def search(self, collection, query_embedding, top_k=10, filters=None, min_score=None):
        return []

    async def delete(self, collection, ids):
        pass

    async def collections(self):
        return []


def get_vector_store(database_url: str) -> VectorStore:
    if database_url.startswith("postgresql"):
        return PgVectorStore()
    return SqliteVecStore()
