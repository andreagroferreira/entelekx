"""Tests for real tool implementations."""

from __future__ import annotations

import pytest

from entelekx_backend.tools.registry import registry


@pytest.mark.asyncio
async def test_read_file(tmp_path):
    file_path = tmp_path / "hello.txt"
    file_path.write_text("world", encoding="utf-8")
    fn = registry.get_fn("read_file")
    assert fn is not None
    result = await fn(path=str(file_path))
    assert result.status == "success"
    assert result.output == "world"


@pytest.mark.asyncio
async def test_read_file_not_found():
    fn = registry.get_fn("read_file")
    result = await fn(path="/nonexistent/path/file.txt")
    assert result.status == "error"


@pytest.mark.asyncio
async def test_write_file(tmp_path):
    file_path = tmp_path / "out.txt"
    fn = registry.get_fn("write_file")
    result = await fn(path=str(file_path), content="data")
    assert result.status == "success"
    assert file_path.read_text(encoding="utf-8") == "data"


@pytest.mark.asyncio
async def test_list_dir(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b").mkdir()
    fn = registry.get_fn("list_dir")
    result = await fn(path=str(tmp_path))
    assert result.status == "success"
    names = {entry["name"] for entry in result.output}
    assert "a.txt" in names
    assert "b" in names


@pytest.mark.asyncio
async def test_run_command():
    fn = registry.get_fn("run_command")
    result = await fn(command="echo hello")
    assert result.status == "success"
    assert "hello" in result.output


@pytest.mark.asyncio
async def test_web_search_stub():
    fn = registry.get_fn("web_search")
    result = await fn(query="EntelekX")
    assert result.status == "success"
    assert result.output["query"] == "EntelekX"


@pytest.mark.asyncio
async def test_ask_user():
    fn = registry.get_fn("ask_user")
    result = await fn(question="What is your name?")
    assert result.status == "success"
    assert result.output["question"] == "What is your name?"


def test_registry_metadata():
    assert "read_file" in registry.list_tools()
    assert "write_file" in registry.list_tools()
    assert "run_command" in registry.list_tools()
    definitions = registry.definitions()
    assert any(d["function"]["name"] == "read_file" for d in definitions)
