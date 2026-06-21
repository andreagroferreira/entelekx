"""Tool registry with schemas, risk levels and real implementations."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ToolResult:
    status: str  # success, error, blocked
    output: str | dict[str, Any]
    error: str | None = None


@dataclass
class ToolInfo:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable[..., Coroutine[Any, Any, ToolResult]]
    risk: str = "low"  # low, medium, high
    requires_approval: bool = False


class ToolRegistry:
    """Registry of tools with metadata and runtime dispatch."""

    def __init__(self):
        self._tools: dict[str, ToolInfo] = {}

    def register(self, tool: ToolInfo) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolInfo | None:
        return self._tools.get(name)

    def get_fn(self, name: str) -> Callable[..., Coroutine[Any, Any, ToolResult]] | None:
        info = self._tools.get(name)
        return info.fn if info else None

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def definitions(self) -> list[dict[str, Any]]:
        """Return tool definitions for provider APIs."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    def metadata(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "risk": t.risk,
                "requires_approval": t.requires_approval,
            }
            for t in self._tools.values()
        ]


registry = ToolRegistry()


async def read_file(path: str) -> ToolResult:
    try:
        target = Path(path).expanduser()
        if not target.exists():
            return ToolResult(status="error", output="", error=f"File not found: {path}")
        content = target.read_text(encoding="utf-8", errors="replace")
        return ToolResult(status="success", output=content)
    except Exception as exc:
        return ToolResult(status="error", output="", error=str(exc))


async def write_file(path: str, content: str) -> ToolResult:
    try:
        target = Path(path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return ToolResult(status="success", output=f"Wrote {len(content)} bytes to {path}")
    except Exception as exc:
        return ToolResult(status="error", output="", error=str(exc))


async def list_dir(path: str = ".") -> ToolResult:
    try:
        target = Path(path).expanduser()
        if not target.exists():
            return ToolResult(status="error", output="", error=f"Path not found: {path}")
        if not target.is_dir():
            return ToolResult(status="error", output="", error=f"Not a directory: {path}")
        entries = []
        for entry in target.iterdir():
            entries.append({"name": entry.name, "type": "directory" if entry.is_dir() else "file"})
        return ToolResult(status="success", output=entries)
    except Exception as exc:
        return ToolResult(status="error", output="", error=str(exc))


async def run_command(command: str, cwd: str | None = None, timeout: int = 30) -> ToolResult:
    """Run a shell command in a restricted way."""
    try:
        workdir = Path(cwd).expanduser() if cwd else Path.cwd()
        result = subprocess.run(
            command,
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PATH": os.environ.get("PATH", "")},
        )
        return ToolResult(
            status="success" if result.returncode == 0 else "error",
            output=result.stdout,
            error=result.stderr if result.stderr else None,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(status="error", output="", error="Command timed out")
    except Exception as exc:
        return ToolResult(status="error", output="", error=str(exc))


async def web_search(query: str, max_results: int = 5) -> ToolResult:
    """Stub web search: returns a formatted query string."""
    try:
        # In production, wire to a search provider (DuckDuckGo, SerpAPI, etc.).
        return ToolResult(
            status="success",
            output={
                "query": query,
                "max_results": max_results,
                "results": [],
                "note": "Web search provider not configured. Configure a search API to enable live results.",
            },
        )
    except Exception as exc:
        return ToolResult(status="error", output="", error=str(exc))


async def ask_user(question: str) -> ToolResult:
    """Placeholder tool that signals the UI to ask the user a question."""
    return ToolResult(
        status="success",
        output={"question": question, "note": "Waiting for user response via UI."},
    )


registry.register(
    ToolInfo(
        name="read_file",
        description="Read the contents of a file at the given path.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative or absolute file path"},
            },
            "required": ["path"],
        },
        fn=read_file,
    )
)

registry.register(
    ToolInfo(
        name="write_file",
        description="Write content to a file at the given path.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative or absolute file path"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
        fn=write_file,
        risk="medium",
        requires_approval=True,
    )
)

registry.register(
    ToolInfo(
        name="list_dir",
        description="List files and directories inside a directory.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path"},
            },
            "required": ["path"],
        },
        fn=list_dir,
    )
)

registry.register(
    ToolInfo(
        name="run_command",
        description="Run a shell command with a timeout. Destructive commands require approval.",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"},
                "cwd": {"type": "string", "description": "Working directory"},
                "timeout": {"type": "integer", "description": "Timeout in seconds"},
            },
            "required": ["command"],
        },
        fn=run_command,
        risk="high",
        requires_approval=True,
    )
)

registry.register(
    ToolInfo(
        name="web_search",
        description="Search the web for the given query.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Maximum number of results"},
            },
            "required": ["query"],
        },
        fn=web_search,
    )
)

registry.register(
    ToolInfo(
        name="ask_user",
        description="Ask the user a clarifying question.",
        parameters={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Question to ask the user"},
            },
            "required": ["question"],
        },
        fn=ask_user,
    )
)
