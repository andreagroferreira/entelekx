"""Anthropic provider adapter."""

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


class AnthropicAdapter(ProviderAdapter):
    """Anthropic Messages API adapter with streaming."""

    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _to_anthropic_messages(self, messages: list[ProviderMessage]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for m in messages:
            if m.role == "tool":
                out.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": m.tool_call_id,
                                "content": m.content,
                            }
                        ],
                    }
                )
            elif m.role == "assistant" and m.tool_calls:
                tool_use_blocks: list[dict[str, Any]] = []
                for tc in m.tool_calls:
                    tool_use_blocks.append(
                        {
                            "type": "tool_use",
                            "id": tc.get("id", ""),
                            "name": tc.get("function", {}).get("name", ""),
                            "input": tc.get("function", {}).get("arguments", {}),
                        }
                    )
                out.append({"role": "assistant", "content": tool_use_blocks})
            else:
                out.append({"role": m.role, "content": m.content})
        return out

    async def chat_stream(
        self,
        messages: list[ProviderMessage],
        model: str,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[StreamChunk]:
        system_message = ""
        conversation: list[dict[str, Any]] = []
        for m in messages:
            if m.role == "system":
                system_message = m.content
            else:
                conversation.append({"role": m.role, "content": m.content})

        payload: dict[str, Any] = {
            "model": model,
            "messages": self._to_anthropic_messages(messages),
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens if max_tokens is not None else 4096,
        }
        if system_message:
            payload["system"] = system_message
        if tools:
            payload["tools"] = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.parameters,
                }
                for t in tools
            ]

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        async with (
            httpx.AsyncClient(timeout=120.0) as client,
            client.stream(
                "POST",
                f"{self.base_url}/v1/messages",
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
        event_type = parsed.get("type")
        if event_type == "content_block_delta":
            delta = parsed.get("delta", {})
            if delta.get("type") == "text_delta":
                return StreamChunk(delta=delta.get("text", ""))
            if delta.get("type") == "input_json_delta":
                return StreamChunk(delta="")
        if event_type == "content_block_stop":
            return StreamChunk(delta="")
        if event_type == "message_stop":
            return StreamChunk(delta="", finish_reason="stop")
        return None

    def supports_tools(self) -> bool:
        return True
