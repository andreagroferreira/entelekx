# ADR-001: Stack — Python/FastAPI + Nuxt + Electron

## Status

Approved

## Context

EntelekX needs:
- A backend that can orchestrate AI models, run tools and manage state.
- A modern web UI for chat, studio, life OS and settings.
- A desktop app for local-first, two-minute installation.

## Decision

- **Backend:** Python 3.12+ with FastAPI and Pydantic 2.
- **Frontend:** Nuxt 4 with Nuxt UI 4, Vue 3 and TypeScript.
- **Desktop shell:** Electron, which hosts the Nuxt SPA and spawns the Python backend.

## Consequences

### Positive

- FastAPI gives async APIs, auto-generated OpenAPI docs and excellent DX.
- Nuxt 4 is opinionated, fast to build and has a strong Vue/Nuxt UI ecosystem.
- Electron has the largest community, mature auto-updater and easy Python integration.
- TypeScript across frontend gives type safety.
- Python backend leverages the rich AI/ML ecosystem.

### Negative

- Electron apps are larger than Tauri alternatives.
- Two runtimes (Node/Electron + Python) increase packaging complexity.

## Alternatives Considered

- **Tauri** for desktop: lighter but smaller ecosystem; passed due to need for rapid cross-platform maturity and auto-updates.
- **Next.js** for frontend: excellent but Nuxt UI 4 and Vue 3 align better with existing internal skills and ArkaOS patterns.
- **Go/Rust backend:** faster but less AI ecosystem; Python is the pragmatic choice.

## Related

- [[../10_Architecture/02_Technical_Stack]]
- [[ADR-003_Desktop_App_Electron]]
