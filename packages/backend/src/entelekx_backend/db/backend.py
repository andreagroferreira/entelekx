"""Database backend abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel


class DatabaseBackend(ABC):
    """Abstract async database backend for PostgreSQL and SQLite."""

    def __init__(self, url: str):
        self.url = url
        self._engine = create_async_engine(url, echo=False, future=True)

    @abstractmethod
    async def connect(self) -> None:
        """Validate connectivity and create schema if needed."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the engine pool."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if database is reachable."""

    @abstractmethod
    async def create_database_if_not_exists(self) -> None:
        """Create the database (only meaningful for local Postgres)."""

    @abstractmethod
    async def enable_vector_extension(self) -> None:
        """Enable vector extension (pgvector or sqlite-vec)."""

    @abstractmethod
    def get_session(self) -> AsyncSession:
        """Return a new async session."""

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session = self.get_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class PostgresBackend(DatabaseBackend):
    """PostgreSQL + pgvector backend."""

    async def connect(self) -> None:
        pass  # Migrations handle schema creation

    async def disconnect(self) -> None:
        await self._engine.dispose()

    async def health_check(self) -> bool:
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text('SELECT 1'))
            return True
        except Exception:
            return False

    async def create_database_if_not_exists(self) -> None:
        # Implemented by the setup wizard / installer
        pass

    async def enable_vector_extension(self) -> None:
        async with self._engine.begin() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

    def get_session(self) -> AsyncSession:
        from sqlalchemy.orm import sessionmaker

        AsyncSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine, class_=AsyncSession
        )
        return AsyncSessionLocal()


class SQLiteBackend(DatabaseBackend):
    """SQLite + sqlite-vec backend."""

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        await self._engine.dispose()

    async def health_check(self) -> bool:
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text('SELECT 1'))
            return True
        except Exception:
            return False

    async def create_database_if_not_exists(self) -> None:
        pass

    async def enable_vector_extension(self) -> None:
        import sqlite_vec

        async with self._engine.begin() as conn:
            await conn.connection.run_sync(
                lambda db: db.enable_load_extension(True)
            )
            await conn.connection.run_sync(
                lambda db: db.load_extension(sqlite_vec.loadable_path())
            )

    def get_session(self) -> AsyncSession:
        from sqlalchemy.orm import sessionmaker

        AsyncSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine, class_=AsyncSession
        )
        return AsyncSessionLocal()


def get_database_backend(url: str | None = None) -> DatabaseBackend:
    from entelekx_backend.core.config import get_settings

    resolved = url or get_settings().resolved_database_url
    if resolved.startswith("postgresql") or resolved.startswith("postgres"):
        return PostgresBackend(resolved)
    if resolved.startswith("sqlite"):
        return SQLiteBackend(resolved)
    raise ValueError(f"Unsupported database URL: {resolved}")
