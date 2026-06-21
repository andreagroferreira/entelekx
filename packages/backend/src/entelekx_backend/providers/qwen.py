"""Qwen provider adapter (OpenAI-compatible)."""

from __future__ import annotations

from entelekx_backend.providers.openai import OpenAICompatibleAdapter


class QwenAdapter(OpenAICompatibleAdapter):
    """Qwen API adapter using OpenAI-compatible endpoint."""

    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"):
        super().__init__(api_key, base_url)
