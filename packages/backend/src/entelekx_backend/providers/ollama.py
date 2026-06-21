"""Ollama provider adapter."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import httpx

from entelekx_backend.providers.base import (
    ProviderAdapter,
    ProviderMessage,
    StreamChunk,
    ToolDefinition,
)


class OllamaAdapter(ProviderAdapter):
    """Ollama chat completion adapter using httpx streaming."""

    def __init__(self, base_url: str = "http://127.0.0.1:11434"):
        self.base_url = base_url.rstrip("/")

    async def chat_stream(
        self,
        messages: list[ProviderMessage],
        model: str,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[StreamChunk]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "options": {"temperature": temperature},
        }
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in tools
            ]

        async with httpx.AsyncClient(timeout=120.0) as client, client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    parsed = self._parse_line(line)
                except Exception:
                    continue
                if parsed:
                    yield parsed

    def _parse_line(self, line: str) -> StreamChunk | None:
        import json

        parsed = json.loads(line)
        content = parsed.get("message", {}).get("content", "")
        tool_calls = parsed.get("message", {}).get("tool_calls")
        normalized = None
        if tool_calls:
            normalized = [
                {
                    "id": tc.get("function", {}).get("name", "") + "_call",
                    "type": "function",
                    "function": {
                        "name": tc.get("function", {}).get("name", ""),
                        "arguments": tc.get("function", {}).get("arguments", {}),
                    },
                }
                for tc in tool_calls
            ]
        done = parsed.get("done", False)
        finish_reason = "stop" if done else None
        return StreamChunk(delta=content, tool_calls=normalized, finish_reason=finish_reason)

    def supports_tools(self) -> bool:
        return True
