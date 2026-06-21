"""MiniMax provider adapter."""

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


class MiniMaxAdapter(ProviderAdapter):
    """MiniMax chat completion adapter."""

    def __init__(
        self,
        api_key: str,
        group_id: str | None = None,
        base_url: str = "https://api.minimaxi.chat/v1",
    ):
        self.api_key = api_key
        self.group_id = group_id or ""
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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.group_id:
            headers["Group-Id"] = self.group_id

        async with (
            httpx.AsyncClient(timeout=120.0) as client,
            client.stream(
                "POST",
                f"{self.base_url}/text/chatcompletion_v2",
                json=payload,
                headers=headers,
            ) as response,
        ):
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
        choices = parsed.get("choices", [])
        if not choices:
            return None
        delta = choices[0].get("delta", "")
        finish_reason = choices[0].get("finish_reason")
        return StreamChunk(delta=delta, finish_reason=finish_reason)

    def supports_tools(self) -> bool:
        return False
