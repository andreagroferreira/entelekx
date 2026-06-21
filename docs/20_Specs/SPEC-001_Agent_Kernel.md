---
type: spec
status: draft
feature: agent-kernel
project: entelekx
date_created: 2026-06-21
tags: [spec, entelekx, agent, ai, core]
---

# SPEC-001: Agent Kernel

## Overview

**Problem:** EntelekX needs a reliable, streaming conversation loop that can talk to multiple model providers, dispatch tools safely and learn from interactions.

**Goal:** Implement the core Agent Kernel: prompt building, provider routing, streaming, tool dispatch, memory extraction and safety limits.

**Actors:**
- User (sends messages).
- Agent Kernel (orchestrates the loop).
- Provider adapters (OpenRouter, OpenAI, Anthropic, Ollama, etc.).
- Tool implementations (file, shell, browser, etc.).
- Memory/RAG layer.

## Scope

### In scope

- Multi-provider chat API.
- Streaming responses via SSE.
- Tool registry and dispatch.
- Conversation loop with iteration/token limits.
- Approval gate for destructive tools.
- Memory extraction and retrieval.
- Context compression when budget exceeded.
- Session persistence.

### Out of scope

- Fusion Engine (SPEC-002).
- Dev Studio tools (SPEC-003, partial).
- Omnichannel messaging (Phase 6).
- Advanced planning/reasoning agents (future).

## Acceptance Criteria

1. **Given** a configured provider, **when** the user sends a message, **then** the assistant streams a response.
2. **Given** a tool call request, **when** the tool executes, **then** the result is appended and the loop continues.
3. **Given** a destructive tool (write_file, run_command), **when** invoked, **then** the UI shows an approval prompt before execution.
4. **Given** max iterations reached, **when** the loop would continue, **then** it stops and returns a final message.
5. **Given** token budget exceeded, **when** context is too long, **then** older messages are compressed/summarised.
6. **Given** a conversation, **when** it ends, **then** relevant memories are proposed for storage.
7. **Given** a session, **when** the user returns, **then** all messages and state are restored.

## Data Model

### `sessions` table

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK to projects |
| title | str | Auto-generated or user-edited |
| model | str | Provider/model slug |
| settings | jsonb | Temperature, etc. |
| created_at | datetime | |
| updated_at | datetime | |

### `messages` table

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| session_id | uuid | FK |
| role | enum | `system`, `user`, `assistant`, `tool` |
| content | text | Text content |
| tool_calls | jsonb | Tool calls (assistant) |
| tool_call_id | str | ID for tool response matching |
| metadata | jsonb | Tokens, latency, model, etc. |
| created_at | datetime | |

### `tool_calls` table

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| message_id | uuid | FK |
| name | str | Tool name |
| arguments | jsonb | Tool arguments |
| result | jsonb | Tool result |
| status | enum | `pending`, `running`, `success`, `error`, `blocked` |
| approved_by | str | `user`, `auto`, `policy` |
| started_at | datetime | |
| completed_at | datetime | |

## API Contracts

### `POST /api/v1/sessions`

Create a new session.

**Request:**
```json
{
  "project_id": "uuid",
  "title": "Landing page ideation",
  "model": "openrouter/anthropic/claude-sonnet-4"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "title": "Landing page ideation",
  "model": "openrouter/anthropic/claude-sonnet-4",
  "created_at": "2026-06-21T20:00:00Z"
}
```

### `POST /api/v1/sessions/{id}/messages`

Send a message and stream the response via SSE.

**Request:**
```json
{
  "content": "Help me design a landing page for my SaaS"
}
```

**SSE events:**
- `message.delta` — streamed token.
- `tool.call` — tool call requested.
- `tool.approval` — waiting for user approval.
- `tool.result` — tool execution result.
- `message.complete` — final message.
- `error` — error event.

### `POST /api/v1/tool-approval/{tool_call_id}`

Approve or reject a pending tool call.

**Request:**
```json
{ "approved": true }
```

### `GET /api/v1/sessions/{id}/messages`

List messages in a session.

## UI/UX Requirements

### Chat UI

- Message list (user right, assistant left).
- Streaming indicator.
- Tool call cards (collapsible):
  - Pending approval: approve/reject buttons.
  - Running: spinner.
  - Success: summary + expand for full output.
  - Error: red badge.
- New chat button.
- Session sidebar.
- Model selector in toolbar.

### Tool approval UI

- Modal or inline banner showing:
  - Tool name.
  - Arguments.
  - Risk level (low/medium/high).
  - Approve once / approve always for this session / reject.

## Edge Cases

1. **Provider timeout:** retry once with fallback model, then show error.
2. **Tool error:** capture error and let the model retry or explain.
3. **Approval timeout:** cancel tool call and inform model.
4. **Loop runaway:** hard stop at max iterations.
5. **Context too long:** compress oldest non-system messages.
6. **Invalid tool name:** return error to model, do not crash.
7. **Streaming interrupted:** client reconnects to SSE and resumes from last event ID.

## Test Scenarios

| # | Scenario | Type | Expected |
|---|---|---|---|
| 1 | Simple chat with OpenRouter | E2E | Streamed response |
| 2 | Chat with local Ollama | E2E | Streamed response |
| 3 | Tool call and result loop | Integration | Tool executes, loop continues |
| 4 | Destructive tool approval | E2E | UI prompts, execution waits |
| 5 | Max iterations stop | Unit | Loop terminates |
| 6 | Token budget compression | Unit | Old messages summarised |
| 7 | Memory extraction proposed | Integration | Relevant memory shown to user |
| 8 | Session restore | Integration | All messages loaded |
| 9 | Provider failure fallback | Integration | Uses fallback model |

## Dependencies

- [ ] Database abstraction (SPEC-006).
- [ ] Vector store abstraction (SPEC-007).
- [ ] Provider adapters implemented.
- [ ] Tool registry implemented.
- [ ] Security model (path confinement, sandbox).

## Open Questions

- Should tool approval be per-session, per-project or global?
- Should context compression happen automatically or be user-configurable?
- Should memory extraction run in the background or synchronously?

## Related

- [[SPEC-002_Fusion_Engine]]
- [[10_Architecture/06_Agent_Runtime]]
- [[12_Security_Model]]
