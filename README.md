# EntelekX

> The personal AI operating system for builders who want to think, build, decide and ship — in one place.

EntelekX is a **self-hosted, open-source AI workspace** that combines a life assistant, a development studio, a native multi-model deliberation engine and a media forge into a single coherent environment.

## Why EntelekX?

Today, a solo founder or small team uses a dozen tools:
- ChatGPT / Claude / Cursor for conversations
- Notion / ClickUp / Linear for planning
- Figma / Canva for design
- Cursor / VS Code for code
- Midjourney / Runway for media
- A dozen APIs and subscriptions

EntelekX unifies these into one context-aware, local-first operating system. It does not replace your judgment — it amplifies your output.

## What Makes It Different

| Capability | EntelekX |
|---|---|
| **Native Fusion Engine** | Run a panel of models + a judge for better decisions |
| **Dev Studio** | Scaffold, code, test and deploy real apps |
| **Life OS** | Notes, tasks, calendar, goals, decisions, knowledge graph |
| **Adaptive Context** | The system learns you and personalises every prompt |
| **Media Forge** | Generate images, video, audio, 3D and design assets |
| **Self-Hosted Sovereignty** | Your data, your models, your machine |
| **Model Freedom** | OpenRouter, OpenAI, Anthropic, Ollama, Qwen, Kimi, MiniMax and more |

## Quick Start (macOS Desktop App — Recommended)

1. Download the latest `.dmg` from [Releases](https://github.com/andreagroferreira/entelekx/releases).
2. Drag EntelekX to Applications and open it.
3. The setup wizard will configure Postgres (or fall back to SQLite) in under 2 minutes.
4. Add your OpenRouter key (or choose a local model).
5. Start building.

## Command-Line Install

```bash
curl -fsSL https://get.entelekx.ai | bash
```

## Docker Install (Advanced / VPS)

```bash
git clone https://github.com/andreagroferreira/entelekx.git
cd entelekx
cp .env.example .env
cd docker
docker compose up -d --build
```

## Development

### Monorepo structure

```
apps/
  desktop/      # Electron desktop shell
  web/          # Nuxt 4 SPA
packages/
  backend/      # FastAPI Python backend
  shared/       # Shared TypeScript contracts
docs/           # Planning docs, specs, ADRs
```

### Install dependencies

```bash
pnpm install
uv sync --project packages/backend --extra dev
```

### Run backend

```bash
pnpm backend:dev
```

### Run web app

```bash
pnpm dev:web
```

### Run desktop app

```bash
pnpm dev
```

## Architecture

- **Desktop shell:** Electron
- **Frontend:** Nuxt 4 + Vue 3 + TypeScript
- **Backend:** FastAPI + Pydantic 2 + Python 3.12+
- **Database:** PostgreSQL 16+ + pgvector (default), SQLite + sqlite-vec (fallback)
- **Desktop default:** macOS (Windows and Linux coming soon)

## Roadmap

| Phase | Focus |
|---|---|
| Phase 0 | Foundation: repo, Electron shell, FastAPI backend, DB abstraction |
| Phase 1 | Agent Kernel: multi-provider chat, tools, memory |
| Phase 2 | Fusion Engine: multi-model deliberation |
| Phase 3 | Dev Studio: scaffolding, editor, tests, deploy |
| Phase 4 | Life OS: notes, tasks, goals, decisions |
| Phase 5 | Adaptive Context: learning user and project models |
| Phase 6 | Media Forge + Omnichannel messaging |

## Documentation

Full planning and architecture documentation lives in `docs/`:

- `01_Vision.md`
- `02_Personas.md`
- `03_Competitive_Landscape.md`
- `10_Architecture/`
- `20_Specs/`
- `30_Decisions/`
- `40_Roadmap/`

## Status

EntelekX is in early development (Phase 0). Expect rapid iteration.

## License

MIT — see [LICENSE](LICENSE).

## Contribute

We welcome contributions. Start with the specs in `docs/20_Specs/` and the roadmap in `docs/40_Roadmap/`. Open an issue before large changes.
