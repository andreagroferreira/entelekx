# ADR-003: Desktop App — Electron

## Status

Approved

## Context

EntelekX targets macOS first with a two-minute setup. The desktop app must spawn a Python backend, manage a database, auto-update and load a web UI.

## Decision

Use **Electron** for the desktop shell.

## Consequences

### Positive

- Largest ecosystem and documentation.
- Mature auto-updater (`electron-updater`).
- Easy to spawn and manage a Python child process.
- Cross-platform (macOS, Windows, Linux) from one codebase.
- Packaging via `electron-builder`.

### Negative

- Larger installer size than Tauri.
- Higher baseline memory usage.

## Alternatives Considered

- **Tauri:** lighter but smaller community; auto-updater and cross-platform packaging less mature.
- **Native Swift app:** macOS-only, harder to port to Windows/Linux.

## Related

- [[../10_Architecture/13_Desktop_App_Architecture]]
- [[ADR-001_Stack_Python_FastAPI_Nuxt]]
- [[ADR-009_Electron_Backend_Spawn_Model]]
