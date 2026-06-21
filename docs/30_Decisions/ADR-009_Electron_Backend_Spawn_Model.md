# ADR-009: Electron Backend Spawn Model

## Status

Approved

## Context

EntelekX has a TypeScript/Electron desktop shell and a Python/FastAPI backend. The Electron app must manage the backend lifecycle.

## Decision

- Electron main process spawns the Python FastAPI backend as a child process.
- Backend binds to a local port (default 7349, auto-increment if busy).
- Electron monitors backend health via `/api/health` and restarts on crash.
- On app quit, Electron gracefully terminates the backend.
- Renderer window loads the Nuxt SPA from the backend URL.

## Consequences

### Positive

- Single desktop installer.
- Backend lifecycle is transparent to the user.
- Easy to restart/update backend independently.

### Negative

- Need to package Python runtime + dependencies with the app.
- Backend logs must be surfaced to a debug panel.

## Packaging Strategy

- Bundle Python environment via `uv` or standalone virtualenv.
- Ship backend wheel inside the Electron app resources.
- On first run, install/extract backend if needed.

## Alternatives Considered

- **Separate backend installer:** worse UX.
- **Backend as a service:** contradicts self-hosted sovereignty.

## Related

- [[../10_Architecture/13_Desktop_App_Architecture]]
- [[ADR-003_Desktop_App_Electron]]
