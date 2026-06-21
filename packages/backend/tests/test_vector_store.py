"""Integration tests for SPEC-007 vector store abstraction."""

from __future__ import annotations

import pytest

from entelekx_backend.db.backend import get_database_backend
from entelekx_backend.vector.store import (
    VectorSearchResult,
    get_vector_store,
)


@pytest.fixture
async def sqlite_vector_store(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'vectors.db'}"
    backend = get_database_backend(url)
    await backend.connect()
    store = get_vector_store(url, backend._engine, dimension=3)
    await store.initialize()
    yield store
    await backend.disconnect()


@pytest.mark.asyncio
async def test_vector_store_initialization(sqlite_vector_store):
    assert await sqlite_vector_store.collections() == []


@pytest.mark.asyncio
async def test_vector_store_upsert_and_search(sqlite_vector_store):
    await sqlite_vector_store.upsert(
        collection="memories",
        ids=["m1", "m2"],
        texts=["hello world", "goodbye world"],
        embeddings=[[0.1, 0.2, 0.3], [0.9, 0.8, 0.7]],
        metadata=[{"project_id": "p1", "type": "note"}, {"project_id": "p1", "type": "note"}],
    )

    results = await sqlite_vector_store.search(
        collection="memories",
        query_embedding=[0.1, 0.2, 0.3],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].text == "hello world"
    assert 0.99 <= results[0].score <= 1.0
    assert results[0].metadata["rowid"] is not None


@pytest.mark.asyncio
async def test_vector_store_search_with_filters(sqlite_vector_store):
    await sqlite_vector_store.upsert(
        collection="docs",
        ids=["d1", "d2"],
        texts=["alpha", "beta"],
        embeddings=[[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]],
        metadata=[
            {"project_id": "p1", "type": "guide"},
            {"project_id": "p2", "type": "guide"},
        ],
    )

    results = await sqlite_vector_store.search(
        collection="docs",
        query_embedding=[0.1, 0.2, 0.3],
        top_k=10,
        filters={"project_id": "p1"},
    )

    assert len(results) == 1
    assert results[0].text == "alpha"


@pytest.mark.asyncio
async def test_vector_store_delete(sqlite_vector_store):
    await sqlite_vector_store.upsert(
        collection="notes",
        ids=["n1", "n2"],
        texts=["keep me", "delete me"],
        embeddings=[[0.1, 0.2, 0.3], [0.9, 0.8, 0.7]],
        metadata=[{}, {}],
    )

    await sqlite_vector_store.delete("notes", ["n2"])

    results = await sqlite_vector_store.search(
        collection="notes",
        query_embedding=[0.9, 0.8, 0.7],
        top_k=10,
    )

    assert len(results) == 1
    assert results[0].text == "keep me"


@pytest.mark.asyncio
async def test_vector_store_dimension_validation(sqlite_vector_store):
    with pytest.raises(ValueError, match="dimension"):
        await sqlite_vector_store.upsert(
            collection="bad",
            ids=["x1"],
            texts=["text"],
            embeddings=[[0.1, 0.2]],
            metadata=[{}],
        )


@pytest.mark.asyncio
async def test_get_vector_store_factory():
    pg_store = get_vector_store("postgresql://localhost/entelekx", None, dimension=128)
    sqlite_store = get_vector_store("sqlite+aiosqlite:///tmp/x.db", None, dimension=128)
    assert pg_store._dimension == 128
    assert sqlite_store._dimension == 128
    assert isinstance(sqlite_store, VectorSearchResult) is False
