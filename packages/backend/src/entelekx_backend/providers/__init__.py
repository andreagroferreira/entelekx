"""Provider adapter registry."""

from __future__ import annotations

from entelekx_backend.providers.anthropic import AnthropicAdapter
from entelekx_backend.providers.base import EchoAdapter, ProviderAdapter
from entelekx_backend.providers.kimi import KimiAdapter
from entelekx_backend.providers.minimax import MiniMaxAdapter
from entelekx_backend.providers.ollama import OllamaAdapter
from entelekx_backend.providers.openai import OpenAICompatibleAdapter
from entelekx_backend.providers.openrouter import OpenRouterAdapter
from entelekx_backend.providers.qwen import QwenAdapter


class ProviderRegistry:
    """Registry of provider adapters keyed by provider slug."""

    def __init__(self):
        self._adapters: dict[str, ProviderAdapter] = {}

    def register(self, name: str, adapter: ProviderAdapter) -> None:
        self._adapters[name] = adapter

    def get(self, name: str) -> ProviderAdapter | None:
        return self._adapters.get(name)

    def list(self) -> list[str]:
        return list(self._adapters.keys())


def build_provider_registry(
    openrouter_api_key: str | None = None,
    openai_api_key: str | None = None,
    anthropic_api_key: str | None = None,
    qwen_api_key: str | None = None,
    kimi_api_key: str | None = None,
    minimax_api_key: str | None = None,
    minimax_group_id: str | None = None,
    ollama_base_url: str | None = None,
) -> ProviderRegistry:
    registry = ProviderRegistry()
    if openrouter_api_key:
        registry.register("openrouter", OpenRouterAdapter(openrouter_api_key))
    else:
        registry.register("openrouter", EchoAdapter())

    if openai_api_key:
        registry.register("openai", OpenAICompatibleAdapter(openai_api_key))
    else:
        registry.register("openai", EchoAdapter())

    if anthropic_api_key:
        registry.register("anthropic", AnthropicAdapter(anthropic_api_key))
    else:
        registry.register("anthropic", EchoAdapter())

    if qwen_api_key:
        registry.register("qwen", QwenAdapter(qwen_api_key))
    else:
        registry.register("qwen", EchoAdapter())

    if kimi_api_key:
        registry.register("kimi", KimiAdapter(kimi_api_key))
    else:
        registry.register("kimi", EchoAdapter())

    if minimax_api_key:
        registry.register("minimax", MiniMaxAdapter(minimax_api_key, minimax_group_id))
    else:
        registry.register("minimax", EchoAdapter())

    registry.register("ollama", OllamaAdapter(ollama_base_url or "http://127.0.0.1:11434"))
    registry.register("echo", EchoAdapter())
    return registry
