# EntelekX — System Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        User Interfaces                             │
│  Electron Desktop App  ·  Web SPA (Nuxt)  ·  CLI/TUI (future)      │
└───────────────────────────┬───────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                    Electron Main Process                            │
│  - Spawns Python backend (FastAPI)                                  │
│  - Manages Postgres setup / migrations                            │
│  - Auto-updater (electron-updater)                                  │
│  - Opens BrowserWindow with Nuxt SPA                                │
└───────────────────────────┬───────────────────────────────────────┘
                            │ HTTP / WebSocket / SSE
┌───────────────────────────▼───────────────────────────────────────┐
│                    API Gateway (FastAPI)                            │
│  Auth · Sessions · Projects · Webhooks · Server-Sent Events         │
└───────────────────────────┬───────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                       Agent Kernel                                │
│  Conversation Loop · Planner · Tool Dispatch · Memory · Context   │
│  Fusion Engine · Provider Router · Adaptive User Model            │
└───────┬───────────────┬───────────────┬─────────────────────────────┘
        │               │               │
┌───────▼───────┐  ┌────▼────┐  ┌───────▼────────┐
│  Tool Runtime │  │  RAG /  │  │   Adaptive     │
│  (sandboxed)  │  │ Memory  │  │   Context      │
│  Filesystem   │  │ Vector  │  │  User model    │
│  Browser      │  │ Graph   │  │  Project model │
│  Shell / Exec │  │ FTS     │  │  Preference    │
│  MCP / ACI    │  │         │  │  learning      │
└───────────────┘  └─────────┘  └────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────┐
│  Dev Studio Layer                                            │
│  Scaffolding · Code editor · Tests · Git · CI/CD · Deploy    │
└─────────────────────────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────┐
│  Media Forge Layer                                           │
│  Higgsfield MCP · Image · Video · Audio · 3D · Design        │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility |
|---|---|
| Electron main | Lifecycle, updates, Postgres setup, window management |
| Nuxt SPA | UI: chat, studio, life OS, settings, previews |
| FastAPI | API, auth, sessions, SSE streaming, webhooks |
| Agent Kernel | Core AI orchestration: prompts, tools, memory, planning |
| Fusion Engine | Multi-model panel + judge deliberation |
| Tool Runtime | Sandboxed execution of native and MCP tools |
| RAG/Memory | Embeddings, vector search, knowledge graph, FTS |
| Adaptive Context | User model, project model, preference learning |
| Dev Studio | Scaffolding, editing, testing, deployment |
| Media Forge | Media generation and design handoff |

## Data Flow Example: "Build a landing page for my product"

1. User types the request in the Nuxt chat UI.
2. FastAPI receives it and assigns it to the Agent Kernel.
3. Adaptive Context enriches the prompt with user/project context.
4. Agent Kernel decides to use the Fusion Engine for requirements.
5. Fusion panel produces multiple analyses; judge synthesises.
6. Agent Kernel calls Dev Studio to scaffold a Nuxt project.
7. Agent Kernel calls Media Forge to generate hero image.
8. Agent Kernel calls Tool Runtime to write files (sandboxed).
9. User previews the result in the Nuxt UI.
10. User deploys via the Dev Studio deploy helper.

## Related

- [[02_Technical_Stack]]
- [[06_Agent_Runtime]]
- [[07_Fusion_Engine]]
- [[13_Desktop_App_Architecture]]
