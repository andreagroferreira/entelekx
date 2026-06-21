# EntelekX — PROJECT.md

## Project Metadata

| Field | Value |
|---|---|
| Name | EntelekX |
| Type | Open-source personal AI operating system |
| Repository | `https://github.com/andreagroferreira/entelekx` |
| License | MIT |
| Default platform | macOS desktop app |
| Stack | Electron + Nuxt 4 + FastAPI + PostgreSQL/SQLite |
| Status | Phase 0: Foundation |

## Vision

EntelekX is the personal AI operating system for builders who want to think, build, decide and ship — in one place. It unifies a life assistant, development studio, multi-model deliberation engine and media forge into a self-hosted environment.

## Squad

- **PM:** Project founder
- **Backend lead:** AI assistant (OpenCode)
- **Frontend lead:** AI assistant (OpenCode)
- **QA:** AI assistant + future contributors

## Entry Points

- Obsidian planning docs: `Projects/EntelekX/`
- Codebase: this repository
- Default branch: `main`
- Releases: calendar versioning (future)

## Conventions

- **Specs:** required before any code change. Live in `20_Specs/`.
- **ADRs:** required for architectural decisions. Live in `30_Decisions/`.
- **Commits:** conventional commits.
- **Tests:** pytest for Python, Vitest for TypeScript.
- **Code style:** Ruff (Python), ESLint/Prettier (TS).

## MCPs

None yet; to be configured as project evolves.

## Non-Negotiables

1. MIT license.
2. Self-hosted first.
3. Postgres + pgvector default; SQLite + sqlite-vec fallback.
4. Electron desktop shell.
5. Automatic updates.
6. Specs before code.
7. Security: sandboxed execution, secret encryption, network allowlists.

## Quick Links

- [[00_Index]]
- [[10_Architecture/00_Index]]
- [[20_Specs/00_Index]]
- [[40_Roadmap/00_Index]]
