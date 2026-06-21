"""Kimi (Moonshot AI) provider adapter (OpenAI-compatible)."""

from __future__ import annotations

from entelekx_backend.providers.openai import OpenAICompatibleAdapter


class KimiAdapter(OpenAICompatibleAdapter):
    """Kimi API adapter using OpenAI-compatible endpoint."""

    def __init__(self, api_key: str, base_url: str = "https://api.moonshot.cn/v1"):
        super().__init__(api_key, base_url)
