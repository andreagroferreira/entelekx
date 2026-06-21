"""Database backend abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from alembic import command


class DatabaseBackend(ABC):
    """Abstract async database backend for PostgreSQL and SQLite."""

    def __init__(self, url: str):
        self.url = url
        self._engine = None

    async def _ensure_engine(self) -> None:
        """Create the async engine lazily (used by SQLite after sync migrations)."""
        if self._engine is None:
            self._engine = create_async_engine(self.url, echo=False, future=True)

    @abstractmethod
    async def connect(self) -> None:
        """Validate connectivity, create database if needed, run migrations and enable vectors."""

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
    async def run_migrations(self) -> None:
        """Run Alembic migrations on the sync dialect of this URL."""

    @abstractmethod
    def get_session(self) -> AsyncSession:
        """Return a new async session."""

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._engine is None:
            await self.connect()
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
        await self._ensure_engine()
        await self.create_database_if_not_exists()
        await self.run_migrations()
        await self.enable_vector_extension()

    async def disconnect(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()

    async def health_check(self) -> bool:
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def create_database_if_not_exists(self) -> None:
        # Local installation/setup wizard should create DB beforehand.
        # This is a no-op for managed Postgres.
        pass

    async def enable_vector_extension(self) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    async def run_migrations(self) -> None:
        sync_url = self.url
        if sync_url.startswith("postgresql+asyncpg"):
            sync_url = sync_url.replace("postgresql+asyncpg", "postgresql")
        self._run_alembic(sync_url)

    def get_session(self) -> AsyncSession:
        from sqlalchemy.orm import sessionmaker

        async_session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        return async_session_local()

    @staticmethod
    def _run_alembic(url: str) -> None:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", url)
        command.upgrade(alembic_cfg, "head")


class SQLiteBackend(DatabaseBackend):
    """SQLite + sqlite-vec backend."""

    async def connect(self) -> None:
        await self.create_database_if_not_exists()
        # Run migrations on a sync engine with a pre-bound connection so SQLite
        # commits DDL immediately. Then create the async engine.
        await self._run_migrations_on_sync_engine()
        await self._ensure_engine()
        await self.enable_vector_extension()

    async def disconnect(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()

    async def health_check(self) -> bool:
        try:
            await self._ensure_engine()
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def create_database_if_not_exists(self) -> None:
        # Ensure parent directory exists; the file is created by SQLite on first access.
        db_path = self.url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def enable_vector_extension(self) -> None:
        import sqlite_vec

        async with self._engine.connect() as conn:
            raw = await conn.get_raw_connection()
            db = raw.driver_connection
            await db.enable_load_extension(True)
            await db.load_extension(sqlite_vec.loadable_path())

    async def _run_migrations_on_sync_engine(self) -> None:
        sync_url = self.url
        if sync_url.startswith("sqlite+aiosqlite"):
            sync_url = sync_url.replace("sqlite+aiosqlite", "sqlite")
        from sqlalchemy import create_engine, text

        engine = create_engine(sync_url)
        with engine.connect() as conn:
            cfg = Config("alembic.ini")
            cfg.set_main_option("sqlalchemy.url", sync_url)
            cfg.attributes["connection"] = conn
            command.upgrade(cfg, "head")
            conn.execute(text("PRAGMA wal_checkpoint(FULL)"))
        engine.dispose()

    async def run_migrations(self) -> None:
        await self._run_migrations_on_sync_engine()
    def get_session(self) -> AsyncSession:
        from sqlalchemy.orm import sessionmaker

        async_session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        return async_session_local()


    @staticmethod
    def _run_alembic(url: str) -> None:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", url)
        command.upgrade(alembic_cfg, "head")


def get_database_backend(url: str | None = None) -> DatabaseBackend:
    from entelekx_backend.core.config import get_settings

    resolved = url or get_settings().resolved_database_url
    if resolved.startswith("postgresql") or resolved.startswith("postgres"):
        return PostgresBackend(resolved)
    if resolved.startswith("sqlite"):
        return SQLiteBackend(resolved)
    raise ValueError(f"Unsupported database URL scheme: {resolved}")
    raise ValueError(f"Unsupported database URL: {resolved}")
