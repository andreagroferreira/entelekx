"""Agent kernel: streaming conversation loop with tools and safety."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlmodel import select as sqlmodel_select

from entelekx_backend.db.backend import DatabaseBackend, get_database_backend
from entelekx_backend.models import Message, Session, ToolCall
from entelekx_backend.providers.base import ProviderAdapter, ProviderMessage, ToolDefinition
from entelekx_backend.tools.registry import ToolResult, registry


@dataclass
class KernelEvent:
    event: str
    data: dict[str, Any]


class AgentKernel:
    """Streaming agent loop with tool dispatch and approval gates."""

    def __init__(
        self,
        database_url: str,
        provider: ProviderAdapter,
        max_iterations: int = 10,
        token_budget: int = 16000,
    ):
        self.database_url = database_url
        self.provider = provider
        self.max_iterations = max_iterations
        self.token_budget = token_budget
        self._backend: DatabaseBackend | None = None

    async def _get_backend(self) -> DatabaseBackend:
        if self._backend is None:
            self._backend = get_database_backend(self.database_url)
            await self._backend.connect()
        return self._backend

    async def _close(self) -> None:
        if self._backend is not None:
            await self._backend.disconnect()
            self._backend = None

    async def run(
        self,
        session_id: UUID,
        user_message: str,
        tools: list[ToolDefinition] | None = None,
    ) -> AsyncIterator[KernelEvent]:
        backend = await self._get_backend()
        tools = tools or []

        async with backend.session() as session:
            db_session = await session.execute(sqlmodel_select(Session).where(Session.id == session_id))
            chat_session = db_session.scalar_one_or_none()
            if chat_session is None:
                yield KernelEvent("error", {"detail": f"Session {session_id} not found"})
                return

            # Store user message.
            user_msg = Message(session_id=session_id, role="user", content=user_message)
            session.add(user_msg)
            await session.commit()
            await session.refresh(user_msg)
            yield KernelEvent("message.user", {"id": str(user_msg.id), "content": user_message})

            iteration = 0
            while iteration < self.max_iterations:
                iteration += 1
                messages = await self._load_messages(session, session_id)
                provider_messages = self._to_provider_messages(messages)

                assistant_content_parts: list[str] = []
                pending_tool_calls: list[dict[str, Any]] = []
                finish_reason: str | None = None

                stream = self.provider.chat_stream(
                    provider_messages,
                    model=chat_session.model or "echo",
                    tools=tools if self.provider.supports_tools() else None,
                )

                async for chunk in stream:
                    if chunk.delta:
                        assistant_content_parts.append(chunk.delta)
                        yield KernelEvent("message.delta", {"delta": chunk.delta})
                    if chunk.tool_calls:
                        pending_tool_calls.extend(chunk.tool_calls)
                    if chunk.finish_reason:
                        finish_reason = chunk.finish_reason

                assistant_content = "".join(assistant_content_parts)

                # Tool calls requested?
                tool_calls_to_record: list[dict[str, Any]] = []
                for tc in pending_tool_calls:
                    name = tc.get("function", {}).get("name", "")
                    args_raw = tc.get("function", {}).get("arguments", "")
                    try:
                        args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                    except json.JSONDecodeError:
                        args = {}
                    tool_calls_to_record.append({
                        "id": tc.get("id", ""),
                        "name": name,
                        "arguments": args,
                    })

                if tool_calls_to_record:
                    assistant_msg = Message(
                        session_id=session_id,
                        role="assistant",
                        content=assistant_content,
                        tool_calls=tool_calls_to_record,
                    )
                    session.add(assistant_msg)
                    await session.commit()
                    await session.refresh(assistant_msg)
                    yield KernelEvent("message.tool_calls", {
                        "message_id": str(assistant_msg.id),
                        "tool_calls": tool_calls_to_record,
                    })

                    for tc in tool_calls_to_record:
                        name = tc["name"]
                        args = tc["arguments"]
                        tool_call_id = tc.get("id", "")
                        if self._requires_approval(name):
                            tool_call_row = ToolCall(
                                session_id=session_id,
                                message_id=assistant_msg.id,
                                name=name,
                                arguments=args,
                                status="pending",
                                rationale=f"{name} requires user approval",
                            )
                            session.add(tool_call_row)
                            await session.commit()
                            await session.refresh(tool_call_row)
                            yield KernelEvent("tool.approval", {
                                "tool_call_id": str(tool_call_row.id),
                                "name": name,
                                "arguments": args,
                                "risk": self._risk_level(name),
                            })
                            return

                        result = await self._execute_tool(session, name, args, assistant_msg.id, tool_call_id)
                        yield KernelEvent("tool.result", {
                            "tool_call_id": tool_call_id,
                            "name": name,
                            "status": result.status,
                            "output": result.output,
                            "error": result.error,
                        })
                    continue

                # Plain assistant message.
                assistant_msg = Message(
                    session_id=session_id,
                    role="assistant",
                    content=assistant_content,
                )
                session.add(assistant_msg)
                await session.commit()
                await session.refresh(assistant_msg)
                yield KernelEvent("message.complete", {
                    "id": str(assistant_msg.id),
                    "content": assistant_content,
                    "finish_reason": finish_reason,
                })
                break
            else:
                yield KernelEvent("error", {"detail": "Max iterations reached"})

        await self._close()

    async def _load_messages(self, session, session_id: UUID) -> list[Message]:
        result = await session.execute(
            select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
        )
        return list(result.scalars().all())

    def _to_provider_messages(self, messages: list[Message]) -> list[ProviderMessage]:
        out: list[ProviderMessage] = []
        for m in messages:
            pm = ProviderMessage(role=m.role, content=m.content)
            if m.role == "assistant" and m.tool_calls:
                pm.tool_calls = m.tool_calls
            if m.role == "tool":
                pm.tool_call_id = m.tool_call_id
            out.append(pm)
        return out

    async def _execute_tool(
        self,
        session,
        name: str,
        args: dict[str, Any],
        message_id: UUID,
        tool_call_id: str,
    ) -> ToolResult:
        fn = registry.get(name)
        if fn is None:
            result = ToolResult(status="error", output="", error=f"Unknown tool: {name}")
        else:
            try:
                result = await fn(**args)
            except Exception as exc:
                result = ToolResult(status="error", output="", error=str(exc))

        tool_call_row = ToolCall(
            session_id=message_id,
            message_id=message_id,
            name=name,
            arguments=args,
            result={"status": result.status, "output": result.output, "error": result.error},
            status=result.status,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )
        session.add(tool_call_row)

        tool_msg = Message(
            session_id=message_id,
            role="tool",
            content=json.dumps({"status": result.status, "output": result.output, "error": result.error}),
            tool_call_id=tool_call_id,
        )
        session.add(tool_msg)
        await session.commit()
        return result

    def _requires_approval(self, name: str) -> bool:
        destructive = {"write_file", "run_command", "delete_file", "shell_exec"}
        return name in destructive

    def _risk_level(self, name: str) -> str:
        if name in {"run_command", "shell_exec"}:
            return "high"
        if name in {"write_file", "delete_file"}:
            return "medium"
        return "low"

    async def approve_tool_call(self, tool_call_id: UUID, approved: bool, approved_by: str = "user") -> AsyncIterator[KernelEvent]:
        backend = await self._get_backend()
        async with backend.session() as session:
            result = await session.execute(select(ToolCall).where(ToolCall.id == tool_call_id))
            tc = result.scalar_one_or_none()
            if tc is None:
                yield KernelEvent("error", {"detail": f"Tool call {tool_call_id} not found"})
                return

            if not approved:
                tc.status = "blocked"
                tc.approved_by = approved_by
                await session.commit()
                yield KernelEvent("tool.result", {
                    "tool_call_id": str(tc.id),
                    "name": tc.name,
                    "status": "blocked",
                    "output": "",
                    "error": "User rejected the tool call",
                })
                return

            tc.status = "running"
            tc.started_at = datetime.now(UTC)
            await session.commit()

            result = await self._execute_tool_from_tool_call(session, tc)
            yield KernelEvent("tool.result", {
                "tool_call_id": str(tc.id),
                "name": tc.name,
                "status": result.status,
                "output": result.output,
                "error": result.error,
            })

            # Continue the loop from the same session.
            async for event in self.run(tc.session_id, "", tools=[]):
                yield event

        await self._close()

    async def _execute_tool_from_tool_call(self, session, tc: ToolCall) -> ToolResult:
        fn = registry.get(tc.name)
        if fn is None:
            result = ToolResult(status="error", output="", error=f"Unknown tool: {tc.name}")
        else:
            try:
                result = await fn(**tc.arguments)
            except Exception as exc:
                result = ToolResult(status="error", output="", error=str(exc))

        tc.result = {"status": result.status, "output": result.output, "error": result.error}
        tc.status = result.status
        tc.completed_at = datetime.now(UTC)
        tc.approved_by = "user"

        tool_msg = Message(
            session_id=tc.session_id,
            role="tool",
            content=json.dumps({"status": result.status, "output": result.output, "error": result.error}),
            tool_call_id=str(tc.id),
        )
        session.add(tool_msg)
        await session.commit()
        return result

    async def list_messages(self, session_id: UUID) -> list[Message]:
        backend = await self._get_backend()
        async with backend.session() as session:
            result = await session.execute(
                select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
            )
            return list(result.scalars().all())

    async def compress_context(self, session_id: UUID) -> None:
        """Basic context compression: summarize oldest non-system/tool messages."""
        backend = await self._get_backend()
        async with backend.session() as session:
            result = await session.execute(
                select(Message)
                .where(Message.session_id == session_id, Message.role.in_(["user", "assistant"]))
                .order_by(Message.created_at)
            )
            messages = result.scalars().all()
            if len(messages) <= 4:
                return
            to_summarize = messages[:-4]
            summary = f"[Earlier conversation: {len(to_summarize)} messages summarized]"
            for m in to_summarize:
                await session.delete(m)
            summary_msg = Message(session_id=session_id, role="system", content=summary)
            session.add(summary_msg)
            await session.commit()
        await self._close()

    async def extract_memories(self, session_id: UUID) -> list[str]:
        """Propose simple memories from assistant messages containing facts."""
        backend = await self._get_backend()
        memories: list[str] = []
        async with backend.session() as session:
            result = await session.execute(
                select(Message).where(Message.session_id == session_id, Message.role == "assistant")
            )
            for msg in result.scalars().all():
                if len(msg.content) > 30 and "I" not in msg.content[:20]:
                    memories.append(msg.content[:200])
        await self._close()
        return memories[:3]
