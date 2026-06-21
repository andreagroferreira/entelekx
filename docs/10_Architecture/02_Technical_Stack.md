# EntelekX — Technical Stack

## Overview

| Layer | Technology | Rationale |
|---|---|---|
| Desktop shell | Electron | Large community, mature auto-updater, easy Python subprocess integration |
| Frontend framework | Nuxt 4 | Full-stack Vue, file-based routing, SSR optional, excellent DX |
| UI component library | Nuxt UI 4 | Native Tailwind 4, accessible, fast to build with |
| Frontend language | TypeScript | Type safety across full stack |
| Backend framework | FastAPI | Async Python, excellent Pydantic integration, OpenAPI auto-generation |
| Backend language | Python 3.12+ | Ecosystem AI/ML, readable, fast to prototype |
| Validation / settings | Pydantic 2 + pydantic-settings | Robust config and request validation |
| ORM | SQLModel | Combines SQLAlchemy 2 with Pydantic models |
| Migrations | Alembic | Industry-standard, works with Postgres and SQLite |
| Database default | PostgreSQL 16+ + pgvector | ACID, vectors, full-text, JSONB, mature tooling |
| Database fallback | SQLite + sqlite-vec | Zero-config fallback for users without Postgres |
| Async DB driver | asyncpg (Postgres) / aiosqlite (SQLite) | Async-native |
| Vector abstraction | Custom interface | Swappable pgvector / sqlite-vec / future Qdrant |
| Embeddings | fastembed / sentence-transformers | Local, no API required |
| Task queue | In-process first; Redis optional later | Simplicity in early phases |
| Object storage | Local filesystem | Self-hosted by default; S3/MinIO optional |
| Real-time | SSE / WebSocket | Streaming chat and tool progress |
| Auth | Local bcrypt + 2FA + API tokens | Self-hosted, no external identity required |
| Sandbox | Docker/Podman opt-in | Practical code execution isolation |
| Packaging | Electron Builder, Docker Compose | Desktop and headless deployment |
| Updates | electron-updater + backend auto-update | Mandatory auto-updates |

## Provider Support (MVP)

| Provider | Adapter | Notes |
|---|---|---|
| OpenRouter | OpenAI-compatible | Default; gives access to many models |
| Ollama / local | OpenAI-compatible | Local/self-hosted models |
| OpenAI | Native | Direct API |
| Anthropic | Native | Messages API + prompt caching |
| Qwen | OpenAI-compatible | Alibaba |
| Kimi | OpenAI-compatible | Moonshot |
| MiniMax | OpenAI-compatible | MiniMax |

## Dev Studio Stacks (MVP)

| Stack | Scaffolding | Testing | Deploy target |
|---|---|---|---|
| Laravel | composer + artisan | PHPUnit | VPS / Laravel Cloud |
| Vue 3 / Nuxt 4 | npm + Nuxt CLI | Vitest / Playwright | VPS / Vercel / Netlify |
| Next.js / React | npm + create-next-app | Jest / Playwright | Vercel / VPS |
| Node.js | npm + structure | Vitest / Jest | VPS / Railway / Render |
| Python / FastAPI | uv + FastAPI | pytest | VPS / Docker / Fly |

## Media Layer (Future)

- Higgsfield integration via MCP.
- GPT Image 2, Seedance, Nano Banana, Marketing Studio, etc.
- Local alternatives where available.

## Related

- [[03_Data_Architecture]]
- [[04_Database_Abstraction]]
- [[05_Vector_Store_Abstraction]]
- [[30_Decisions/ADR-001_Stack_Python_FastAPI_Nuxt]]
- [[30_Decisions/ADR-002_Data_Platform_Postgres_pgvector_sqlite_vec]]
- [[30_Decisions/ADR-003_Desktop_App_Electron]]
