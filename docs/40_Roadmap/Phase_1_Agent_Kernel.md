# EntelekX — Phase 1: Agent Kernel

## Estado

**Concluída** ✅

## Goal

Implement the core AI conversation loop with multi-provider support, tool dispatch, memory and streaming.

## Deliverables

- [x] Provider adapter system:
  - [x] OpenRouter
  - [x] Ollama / local
  - [x] OpenAI
  - [x] Anthropic
  - [x] Qwen
  - [x] Kimi
  - [x] MiniMax
- [x] Provider router and configuration UI.
- [x] Conversation loop:
  - [x] Streaming responses.
  - [x] Tool call detection and dispatch.
  - [x] Iteration limits.
  - [x] Token budget (context compression).
- [x] Tool registry with first tools:
  - [x] `read_file`
  - [x] `write_file`
  - [x] `list_dir`
  - [x] `run_command` (sandboxed by timeout)
  - [x] `web_search` (stub)
  - [x] `ask_user`
- [x] Memory extraction and retrieval:
  - [x] Vector search layer ready.
  - [x] Propose memories to user.
- [x] Session persistence.
- [x] Chat UI with streaming and tool progress.
- [x] Approval gate for destructive tools.
- [x] Tests for providers, tools, chat API and kernel loop.

## Out of Scope

- Fusion Engine.
- Dev Studio scaffolding.
- Life OS modules.
- Media generation.

## Definition of Done

A user can install EntelekX, configure an OpenRouter key, send a message, see a streamed response and have a multi-turn conversation with tool execution.

## Related

- [[../20_Specs/SPEC-001_Agent_Kernel]]
- [[../10_Architecture/06_Agent_Runtime]]
