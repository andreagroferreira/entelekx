# EntelekX — Integration Layer

## Goal

Connect EntelekX to the outside world: model providers, tools, agents, services and protocols.

## Provider Adapters

| Provider | Protocol | Status |
|---|---|---|
| OpenRouter | OpenAI-compatible chat completions | MVP default |
| Ollama | OpenAI-compatible local endpoints | MVP |
| OpenAI | Native | MVP |
| Anthropic | Messages API + prompt caching | MVP |
| Qwen | OpenAI-compatible | MVP |
| Kimi (Moonshot) | OpenAI-compatible | MVP |
| MiniMax | OpenAI-compatible | MVP |
| Future providers | Adapter interface | Easy to add |

## Model Context Protocol (MCP)

- EntelekX acts as an **MCP host**: it can connect to external MCP servers.
- EntelekX may expose itself as an **MCP server** for IDEs like Claude Code, Cursor, Windsurf.
- MCP servers for Higgsfield, Open Design, browser, file system, etc.

## Agent Communication Interface (ACI)

- Future protocol for multi-agent orchestration.
- Allows subagents to communicate with clear ownership and handoff.

## Webhooks

- Inbound webhooks for triggers (GitHub, Stripe, etc.).
- Outbound webhooks for notifications and integrations.
- Validation and SSRF protection.

## API

- FastAPI auto-generated OpenAPI schema.
- Versioned API (`/api/v1/`).
- API tokens with scopes.

## IDE Extensions

Future:
- VS Code extension.
- Zed / JetBrains plugin.
- Cursor / Windsurf rules.

## Calendar / Email (Future)

- CalDAV sync.
- IMAP/SMTP email integration.
- Messaging channels (Telegram, Slack, Discord, WhatsApp).

## Related

- [[06_Agent_Runtime]]
- [[07_Fusion_Engine]]
- [[02_Technical_Stack]]
