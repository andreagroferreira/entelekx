"""Tests for the Agent Kernel chat loop and provider adapters."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from entelekx_backend.agent.kernel import AgentKernel, KernelEvent
from entelekx_backend.db.backend import get_database_backend
from entelekx_backend.main import app
from entelekx_backend.models import Message, Project, Session, ToolCall, User
from entelekx_backend.providers.base import EchoAdapter, ProviderMessage, ToolDefinition


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sqlite_url(tmp_path):
    return f"sqlite+aiosqlite:///{tmp_path / 'kernel.db'}"


@pytest.fixture
async def populated_session(sqlite_url):
    backend = get_database_backend(sqlite_url)
    await backend.connect()
    async with backend.session() as session:
        user = User(username=f"user_{uuid4().hex}", password_hash="hash")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        project = Project(user_id=user.id, name="Test", slug="test")
        session.add(project)
        await session.commit()
        await session.refresh(project)

        chat_session = Session(project_id=project.id, title="Chat", model="echo")
        session.add(chat_session)
        await session.commit()
        await session.refresh(chat_session)
        session_id = chat_session.id
        project_id = project.id
    await backend.disconnect()
    return session_id, project_id


@pytest.mark.asyncio
async def test_echo_provider_stream():
    adapter = EchoAdapter()
    messages = [ProviderMessage(role="user", content="hello world")]
    chunks = [chunk async for chunk in adapter.chat_stream(messages, "echo")]
    assert any("hello" in chunk.delta for chunk in chunks)


@pytest.mark.asyncio
async def test_kernel_simple_chat(sqlite_url, populated_session):
    session_id, _ = populated_session
    adapter = EchoAdapter()
    kernel = AgentKernel(sqlite_url, adapter)
    events = [event async for event in kernel.run(session_id, "ping")]

    types = {e.event for e in events}
    assert "message.user" in types
    assert "message.delta" in types
    assert "message.complete" in types


@pytest.mark.asyncio
async def test_kernel_tool_call_requires_approval(sqlite_url, populated_session, monkeypatch):
    session_id, _ = populated_session

    async def fake_stream(messages, model, tools=None, temperature=0.7, max_tokens=None):
        yield KernelEvent(
            "chunk",
            {
                "delta": "",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "write_file",
                            "arguments": '{"path": "/tmp/x.txt", "content": "hi"}',
                        },
                    }
                ],
            },
        )

    class FakeAdapter(EchoAdapter):
        async def chat_stream(self, messages, model, tools=None, temperature=0.7, max_tokens=None):
            yield type(
                "Chunk",
                (),
                {
                    "delta": "",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "write_file",
                                "arguments": '{"path": "/tmp/x.txt", "content": "hi"}',
                            },
                        },
                    ],
                    "finish_reason": None,
                },
            )()

        def supports_tools(self):
            return True

    kernel = AgentKernel(sqlite_url, FakeAdapter())
    events = [
        e
        async for e in kernel.run(
            session_id,
            "write a file",
            tools=[
                ToolDefinition(
                    name="write_file", description="write", parameters={"type": "object"}
                )
            ],
        )
    ]
    assert any(e.event == "tool.approval" for e in events)

    backend = get_database_backend(sqlite_url)
    await backend.connect()
    async with backend.session() as session:
        result = await session.execute(select(ToolCall).where(ToolCall.session_id == session_id))
        assert result.scalars().first() is not None
    await backend.disconnect()


@pytest.mark.asyncio
async def test_kernel_approve_and_continue(sqlite_url, populated_session):
    session_id, _ = populated_session

    class FakeAdapter(EchoAdapter):
        async def chat_stream(self, messages, model, tools=None, temperature=0.7, max_tokens=None):
            for word in ["done"]:
                yield type(
                    "Chunk", (), {"delta": f"{word} ", "tool_calls": None, "finish_reason": "stop"}
                )()

    kernel = AgentKernel(sqlite_url, FakeAdapter())

    # Create a pending tool call manually.
    backend = get_database_backend(sqlite_url)
    await backend.connect()
    async with backend.session() as session:
        msg = Message(
            session_id=session_id,
            role="assistant",
            content="",
            tool_calls=[{"id": "call_1", "name": "read_file", "arguments": {"path": "/tmp/x.txt"}}],
        )
        session.add(msg)
        await session.commit()
        await session.refresh(msg)
        tc = ToolCall(
            session_id=session_id,
            message_id=msg.id,
            name="read_file",
            arguments={"path": "/tmp/x.txt"},
            status="pending",
        )
        session.add(tc)
        await session.commit()
        await session.refresh(tc)
    await backend.disconnect()

    events = [e async for e in kernel.approve_tool_call(tc.id, True)]
    assert any(e.event == "tool.result" for e in events)
    assert any(e.event == "message.complete" for e in events)


def test_create_session_api(client):
    # The API requires an existing project; this test relies on a project not existing.
    response = client.post(
        "/api/v1/sessions",
        json={
            "project_id": str(uuid4()),
            "title": "Test",
            "model": "echo",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_compress_context(sqlite_url, populated_session):
    session_id, _ = populated_session
    backend = get_database_backend(sqlite_url)
    await backend.connect()
    async with backend.session() as session:
        for i in range(6):
            session.add(Message(session_id=session_id, role="user", content=f"msg {i}"))
        await session.commit()
    await backend.disconnect()

    kernel = AgentKernel(sqlite_url, EchoAdapter())
    await kernel.compress_context(session_id)

    backend = get_database_backend(sqlite_url)
    await backend.connect()
    async with backend.session() as session:
        result = await session.execute(
            select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
        )
        remaining = result.scalars().all()
        assert len(remaining) <= 5
        assert any(m.role == "system" and "summarized" in m.content for m in remaining)
    await backend.disconnect()


@pytest.mark.asyncio
async def test_extract_memories(sqlite_url, populated_session):
    session_id, _ = populated_session
    backend = get_database_backend(sqlite_url)
    await backend.connect()
    async with backend.session() as session:
        session.add(
            Message(
                session_id=session_id,
                role="assistant",
                content="The user prefers dark mode for all interfaces.",
            )
        )
        await session.commit()
    await backend.disconnect()

    kernel = AgentKernel(sqlite_url, EchoAdapter())
    memories = await kernel.extract_memories(session_id)
    assert len(memories) >= 1
    assert any("dark mode" in m for m in memories)
