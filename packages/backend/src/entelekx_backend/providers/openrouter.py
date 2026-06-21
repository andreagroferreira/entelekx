"""OpenRouter provider adapter."""

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


class OpenRouterAdapter(ProviderAdapter):
    """OpenRouter chat completion adapter using httpx streaming."""

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
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
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "EntelekX",
        }

        async with httpx.AsyncClient(timeout=120.0) as client, client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    return
                try:
                    chunk = self._parse_chunk(data)
                except Exception:
                    continue
                if chunk:
                    yield chunk

    def _parse_chunk(self, data: str) -> StreamChunk | None:
        import json

        parsed = json.loads(data)
        delta = parsed.get("choices", [{}])[0].get("delta", {})
        content = delta.get("content") or ""
        tool_calls_delta = delta.get("tool_calls")
        tool_calls = None
        if tool_calls_delta:
            tool_calls = [
                {
                    "id": tc.get("id", ""),
                    "type": tc.get("type", "function"),
                    "function": {
                        "name": tc.get("function", {}).get("name", ""),
                        "arguments": tc.get("function", {}).get("arguments", ""),
                    },
                }
                for tc in tool_calls_delta
            ]
        finish_reason = parsed.get("choices", [{}])[0].get("finish_reason")
        return StreamChunk(delta=content, tool_calls=tool_calls, finish_reason=finish_reason)

    def supports_tools(self) -> bool:
        return True
