# EntelekX — Phase 1: Agent Kernel

## Goal

Implement the core AI conversation loop with multi-provider support, tool dispatch, memory and streaming.

## Deliverables

- [ ] Provider adapter system:
  - OpenRouter
  - Ollama / local
  - OpenAI
  - Anthropic
  - Qwen
  - Kimi
  - MiniMax
- [ ] Provider router and configuration UI.
- [ ] Conversation loop:
  - Streaming responses.
  - Tool call detection and dispatch.
  - Iteration limits.
  - Token budget.
- [ ] Tool registry with first tools:
  - `read_file`
  - `write_file`
  - `list_dir`
  - `run_command` (sandboxed)
  - `web_search`
  - `ask_user`
- [ ] Memory extraction and retrieval:
  - Vector search.
  - Propose memories to user.
- [ ] Session persistence.
- [ ] Chat UI with streaming and tool progress.
- [ ] Approval gate for destructive tools.
- [ ] Tests for each provider and tool.

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
