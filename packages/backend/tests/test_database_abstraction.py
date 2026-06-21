"""Integration tests for SPEC-006 database abstraction."""

import pytest
from sqlmodel import select

from entelekx_backend.db.backend import SQLiteBackend, get_database_backend
from entelekx_backend.models import Document, Memory, Message, Project, Session, User


@pytest.fixture
async def sqlite_backend(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'entelekx.db'}"
    backend = get_database_backend(url)
    await backend.connect()
    yield backend
    await backend.disconnect()


@pytest.mark.asyncio
async def test_backend_detects_sqlite(sqlite_backend):
    assert isinstance(sqlite_backend, SQLiteBackend)
    assert await sqlite_backend.health_check() is True


@pytest.mark.asyncio
async def test_migrations_create_tables(sqlite_backend):
    async with sqlite_backend.session() as session:
        result = await session.execute(select(User))
        assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_create_user_project_session(sqlite_backend):
    async with sqlite_backend.session() as session:
        user = User(username="test_user", password_hash="hash")
        session.add(user)
        await session.flush()

        project = Project(user_id=user.id, name="Test", slug="test")
        session.add(project)
        await session.flush()

        chat = Session(project_id=project.id, title="Hello", model="openrouter")
        session.add(chat)
        await session.flush()

        message = Message(session_id=chat.id, role="user", content="Olá")
        session.add(message)
        await session.flush()

        projects = await session.execute(
            select(Project).where(Project.user_id == user.id)
        )
        assert len(projects.scalars().all()) == 1


@pytest.mark.asyncio
async def test_create_memories_and_documents(sqlite_backend):
    async with sqlite_backend.session() as session:
        user = User(username="memory_user", password_hash="hash")
        session.add(user)
        await session.flush()

        project = Project(user_id=user.id, name="Memory Project", slug="memory")
        session.add(project)
        await session.flush()

        memory = Memory(project_id=project.id, content="User likes dark mode", source="chat")
        document = Document(
            project_id=project.id, title="Spec", body="Details", tags=["spec"]
        )
        session.add(memory)
        session.add(document)
        await session.flush()

        docs = await session.execute(
            select(Document).where(Document.project_id == project.id)
        )
        assert docs.scalars().one().tags == ["spec"]
