"""Provider adapter interface for chat completions and streaming."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass
class ProviderMessage:
    role: str
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


@dataclass
class StreamChunk:
    delta: str = ""
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str | None = None


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


class ProviderAdapter(ABC):
    """Abstract adapter for a chat model provider."""

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[ProviderMessage],
        model: str,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Yield streamed chunks for a chat request."""

    @abstractmethod
    def supports_tools(self) -> bool:
        """Return True if this provider can invoke tools."""


class EchoAdapter(ProviderAdapter):
    """Test adapter that echoes the last user message."""

    async def chat_stream(
        self,
        messages: list[ProviderMessage],
        model: str,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[StreamChunk]:
        last = next((m.content for m in reversed(messages) if m.role == "user"), "echo")
        for word in f"Echo: {last}".split():
            yield StreamChunk(delta=f"{word} ")

    def supports_tools(self) -> bool:
        return False
