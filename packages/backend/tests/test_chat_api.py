"""Tests for chat API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from entelekx_backend.core.config import get_settings
from entelekx_backend.db.backend import get_database_backend
from entelekx_backend.main import app
from entelekx_backend.models import Project, Session, User


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def app_project_id():
    settings = get_settings()
    backend = get_database_backend(settings.resolved_database_url)
    asyncio = __import__("asyncio")

    async def setup():
        await backend.connect()
        async with backend.session() as session:
            result = await session.execute(select(User).where(User.username == "chat_api_user"))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(username="chat_api_user", password_hash="hash")
                session.add(user)
                await session.commit()
                await session.refresh(user)
            result = await session.execute(
                select(Project).where(Project.slug == "chat_api_project")
            )
            project = result.scalar_one_or_none()
            if project is None:
                project = Project(user_id=user.id, name="Chat API Project", slug="chat_api_project")
                session.add(project)
                await session.commit()
                await session.refresh(project)
            return str(project.id)

    project_id = asyncio.run(setup())
    yield project_id


@pytest.fixture
async def app_session_id(app_project_id):
    settings = get_settings()
    backend = get_database_backend(settings.resolved_database_url)
    await backend.connect()
    async with backend.session() as session:
        chat_session = Session(
            project_id=__import__("uuid").UUID(app_project_id), title="Chat", model="echo"
        )
        session.add(chat_session)
        await session.commit()
        await session.refresh(chat_session)
        session_id = str(chat_session.id)
    await backend.disconnect()
    return session_id


@pytest.mark.asyncio
async def test_create_session_api(client, app_project_id):
    response = client.post(
        "/api/v1/sessions", json={"project_id": app_project_id, "title": "Chat", "model": "echo"}
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["model"] == "echo"
    assert body["project_id"] == app_project_id


@pytest.mark.asyncio
async def test_send_message_sse(client, app_session_id):
    response = client.post(f"/api/v1/sessions/{app_session_id}/messages", json={"content": "hello"})
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    text = response.text
    assert "message.delta" in text or "message.complete" in text


@pytest.mark.asyncio
async def test_list_messages_api(client, app_session_id):
    response = client.get(f"/api/v1/sessions/{app_session_id}/messages")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
