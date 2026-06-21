# EntelekX — Phase 0: Foundation

## Goal

Set up the project, documentation, CI/CD and the minimal runtime skeleton so subsequent phases can build on solid ground.

## Deliverables

- [ ] Create `wizardingcode/entelekx` GitHub repository.
- [ ] Set up MIT license.
- [ ] Set up monorepo structure:
  - `apps/desktop` (Electron)
  - `apps/web` (Nuxt 4)
  - `packages/backend` (FastAPI Python)
  - `packages/shared` (contracts/types)
  - `docs/`
- [ ] Configure tooling:
  - pnpm workspace
  - Python `pyproject.toml` with `uv`
  - Ruff, pytest, mypy
  - ESLint/Prettier for TypeScript
  - GitHub Actions CI
- [ ] Implement database abstraction layer stubs:
  - `PostgresBackend`
  - `SQLiteBackend`
  - Alembic setup
- [ ] Implement vector store abstraction stubs:
  - `PgVectorStore`
  - `SqliteVecStore`
- [ ] Create Electron main process skeleton:
  - Spawn Python backend.
  - Load Nuxt SPA.
  - Health check.
- [ ] Create Nuxt SPA skeleton:
  - Layout, routing, theme.
  - Chat placeholder page.
- [ ] Create FastAPI skeleton:
  - Health endpoint.
  - Static file serving.
  - Settings/config endpoints.
- [ ] Docker Compose setup (non-default but ready).
- [ ] Headless install script (`install.sh`).
- [ ] Populate all Obsidian documentation (this project).

## Out of Scope

- Real chat.
- Real tools.
- Fusion Engine.
- Dev Studio features.

## Definition of Done

`docker compose up` and the desktop app skeleton both start without errors and serve a hello-world page.

## Related

- [[../20_Specs/SPEC-005_Installation_Wizard]]
- [[../20_Specs/SPEC-006_Database_Abstraction]]
- [[../20_Specs/SPEC-007_Vector_Store_Abstraction]]
