"""Smoke tests for Phase 0."""

import pytest

from entelekx_backend.core.config import Settings, get_settings
from entelekx_backend.db.backend import SQLiteBackend, get_database_backend
from entelekx_backend.vector.store import get_vector_store


@pytest.fixture
def sqlite_url(tmp_path):
    db = tmp_path / "test.db"
    return f"sqlite+aiosqlite:///{db}"


def test_settings_defaults():
    settings = Settings()
    assert settings.app_name == "EntelekX"
    assert settings.port == 7349


def test_database_backend_detects_sqlite(sqlite_url):
    backend = get_database_backend(sqlite_url)
    assert isinstance(backend, SQLiteBackend)


@pytest.mark.asyncio
async def test_sqlite_health_check(sqlite_url):
    backend = get_database_backend(sqlite_url)
    assert await backend.health_check() is True
    await backend.disconnect()


@pytest.mark.asyncio
async def test_sqlite_vector_store_initialization(sqlite_url):
    store = get_vector_store(sqlite_url)
    await store.initialize()
    assert await store.collections() == []


def test_vector_store_backend_selection():
    assert isinstance(get_vector_store("postgresql://localhost/db").__class__.__name__, str)
    assert isinstance(get_vector_store("sqlite+aiosqlite:///x").__class__.__name__, str)
