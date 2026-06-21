"""Tool registry stubs."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    status: str  # success, error, blocked
    output: str | dict[str, Any]
    error: str | None = None


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[..., Coroutine[Any, Any, ToolResult]]] = {}

    def register(
        self,
        name: str,
        fn: Callable[..., Coroutine[Any, Any, ToolResult]],
    ) -> None:
        self._tools[name] = fn

    def get(self, name: str) -> Callable[..., Coroutine[Any, Any, ToolResult]] | None:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())


registry = ToolRegistry()


async def read_file(path: str) -> ToolResult:
    return ToolResult(status="success", output=f"Stub read of {path}")


async def write_file(path: str, content: str) -> ToolResult:
    return ToolResult(status="success", output=f"Stub write to {path}")


registry.register("read_file", read_file)
registry.register("write_file", write_file)
