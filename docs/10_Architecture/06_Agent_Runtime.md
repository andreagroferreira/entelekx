# EntelekX — Agent Runtime

## Overview

The Agent Kernel is the core orchestration layer. It receives a user request, plans, calls models, dispatches tools, updates memory and returns a final response.

## Conversation Loop

```
1. Receive user message + context
2. Enrich prompt with Adaptive Context (user model, project state, memory)
3. Select model(s) via Provider Router
4. Call LLM (streaming)
5. Parse response:
   a. Plain text → stream to user
   b. Tool calls → dispatch tools (sandboxed)
   c. Fusion request → call Fusion Engine
6. Append results to conversation
7. Repeat until done or max iterations
8. Persist session + memory
9. Update Adaptive Context
```

## Key Components

| Component | Responsibility |
|---|---|
| `PromptBuilder` | Assemble system prompt + context + user message |
| `ProviderRouter` | Resolve model name to provider client and credentials |
| `ConversationLoop` | Main async loop |
| `ToolDispatcher` | Route tool calls to native/MCP implementations |
| `ToolPolicy` | Decide which tools are available per project/session |
| `MemoryExtractor` | Derive memories from conversation |
| `ContextCompressor` | Summarise old context when budget is exceeded |

## Tool Categories

| Category | Examples |
|---|---|
| Core | `ask_user`, `think`, `delegate_task`, `summarise` |
| File | `read_file`, `write_file`, `edit_file`, `list_dir`, `search_files` |
| Terminal | `run_command`, `run_test`, `run_linter` |
| Browser | `browser_navigate`, `browser_extract`, `browser_screenshot` |
| Dev | `scaffold_project`, `run_tests`, `deploy_project`, `git_commit` |
| Media | `generate_image`, `generate_video`, `generate_deck` |
| Knowledge | `memory_search`, `memory_add`, `decision_log`, `goal_update` |
| Integrations | `mcp_invoke`, `webhook_send`, `api_call` |

## Safety Limits

- Max tool iterations per request.
- Token budget per request.
- Tool approval gate for destructive operations.
- Path confinement via workspace policy.
- Network egress allowlist.

## Streaming

All assistant responses are streamed via SSE to the UI. Tool progress is also streamed.

## Related

- [[01_System_Diagram]]
- [[07_Fusion_Engine]]
- [[08_Dev_Studio]]
- [[11_Adaptive_Context]]
- [[12_Security_Model]]
- [[20_Specs/SPEC-001_Agent_Kernel]]
