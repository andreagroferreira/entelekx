"""Chat API routers for the agent kernel."""

from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select

from entelekx_backend.agent.kernel import AgentKernel, KernelEvent
from entelekx_backend.core.config import get_settings
from entelekx_backend.db.backend import get_database_backend
from entelekx_backend.models import Project, Session
from entelekx_backend.providers import build_provider_registry
from entelekx_backend.providers.base import ToolDefinition

chat_router = APIRouter(tags=["chat"])


class CreateSessionRequest(BaseModel):
    project_id: UUID
    title: str | None = None
    model: str = "echo"


class CreateSessionResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str | None
    model: str
    created_at: str


@chat_router.post("/sessions", response_model=CreateSessionResponse, status_code=201)
async def create_session(req: CreateSessionRequest):
    settings = get_settings()
    backend = get_database_backend(settings.resolved_database_url)
    await backend.connect()
    async with backend.session() as session:
        project = await session.execute(select(Project).where(Project.id == req.project_id))
        if project.scalar_one_or_none() is None:
            await backend.disconnect()
            raise HTTPException(status_code=404, detail="Project not found")

        chat_session = Session(
            project_id=req.project_id,
            title=req.title,
            model=req.model,
        )
        session.add(chat_session)
        await session.commit()
        await session.refresh(chat_session)
    await backend.disconnect()
    return CreateSessionResponse(
        id=chat_session.id,
        project_id=chat_session.project_id,
        title=chat_session.title,
        model=chat_session.model,
        created_at=chat_session.created_at.isoformat(),
    )


class SendMessageRequest(BaseModel):
    content: str


def _format_sse(event: KernelEvent) -> str:
    data = json.dumps(event.data)
    return f"event: {event.event}\ndata: {data}\n\n"


@chat_router.post("/sessions/{session_id}/messages")
async def send_message(session_id: UUID, req: SendMessageRequest):
    settings = get_settings()
    adapter = _get_provider_adapter(settings)
    kernel = AgentKernel(settings.resolved_database_url, adapter)
    tools = _list_tool_definitions(adapter)

    async def event_generator():
        try:
            async for event in kernel.run(session_id, req.content, tools=tools):
                yield _format_sse(event)
        except Exception as exc:
            yield _format_sse(KernelEvent("error", {"detail": str(exc)}))

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@chat_router.get("/sessions/{session_id}/messages")
async def list_messages(session_id: UUID):
    settings = get_settings()
    adapter = _get_provider_adapter(settings)
    kernel = AgentKernel(settings.resolved_database_url, adapter)
    messages = await kernel.list_messages(session_id)
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "tool_calls": m.tool_calls,
            "tool_call_id": m.tool_call_id,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


class ToolApprovalRequest(BaseModel):
    approved: bool


@chat_router.post("/tool-approval/{tool_call_id}")
async def approve_tool(tool_call_id: UUID, req: ToolApprovalRequest):
    settings = get_settings()
    adapter = _get_provider_adapter(settings)
    kernel = AgentKernel(settings.resolved_database_url, adapter)

    async def event_generator():
        try:
            async for event in kernel.approve_tool_call(tool_call_id, req.approved):
                yield _format_sse(event)
        except Exception as exc:
            yield _format_sse(KernelEvent("error", {"detail": str(exc)}))

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@chat_router.post("/sessions/{session_id}/compress")
async def compress_session(session_id: UUID):
    settings = get_settings()
    adapter = _get_provider_adapter(settings)
    kernel = AgentKernel(settings.resolved_database_url, adapter)
    await kernel.compress_context(session_id)
    return {"status": "ok"}


class CreateProjectRequest(BaseModel):
    name: str
    slug: str
    description: str | None = None


class CreateProjectResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    created_at: str


@chat_router.post("/projects", response_model=CreateProjectResponse, status_code=201)
async def create_project(req: CreateProjectRequest):
    settings = get_settings()
    backend = get_database_backend(settings.resolved_database_url)
    await backend.connect()
    async with backend.session() as session:
        from entelekx_backend.models import User

        user_result = await session.execute(select(User))
        user = user_result.scalars().first()
        if user is None:
            await backend.disconnect()
            raise HTTPException(status_code=400, detail="No user exists; run setup first")
        project = Project(user_id=user.id, name=req.name, slug=req.slug, description=req.description)
        session.add(project)
        await session.commit()
        await session.refresh(project)
    await backend.disconnect()
    return CreateProjectResponse(
        id=project.id,
        name=project.name,
        slug=project.slug,
        created_at=project.created_at.isoformat(),
    )


def _get_provider_adapter(settings):
    registry = build_provider_registry(
        openrouter_api_key=settings.openrouter_api_key,
        openai_api_key=settings.openai_api_key,
        anthropic_api_key=settings.anthropic_api_key,
        qwen_api_key=getattr(settings, "qwen_api_key", None),
        kimi_api_key=getattr(settings, "kimi_api_key", None),
        minimax_api_key=getattr(settings, "minimax_api_key", None),
        minimax_group_id=getattr(settings, "minimax_group_id", None),
        ollama_base_url=settings.ollama_base_url,
    )
    provider = getattr(settings, "default_provider", "echo") or "echo"
    return registry.get(provider) or registry.get("echo")


def _list_tool_definitions(adapter) -> list[ToolDefinition]:
    if not adapter.supports_tools():
        return []
    from entelekx_backend.tools.registry import registry

    definitions: list[ToolDefinition] = []
    for info in registry._tools.values():
        definitions.append(
            ToolDefinition(
                name=info.name,
                description=info.description,
                parameters=info.parameters,
            )
        )
    return definitions
