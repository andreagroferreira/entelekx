"""Provider adapter registry."""

from __future__ import annotations

from entelekx_backend.providers.base import EchoAdapter, ProviderAdapter
from entelekx_backend.providers.ollama import OllamaAdapter
from entelekx_backend.providers.openrouter import OpenRouterAdapter


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
    ollama_base_url: str | None = None,
) -> ProviderRegistry:
    registry = ProviderRegistry()
    if openrouter_api_key:
        registry.register("openrouter", OpenRouterAdapter(openrouter_api_key))
    else:
        registry.register("openrouter", EchoAdapter())
    registry.register("ollama", OllamaAdapter(ollama_base_url or "http://127.0.0.1:11434"))
    registry.register("echo", EchoAdapter())
    return registry
