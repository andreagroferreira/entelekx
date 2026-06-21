# EntelekX — Desktop App Architecture

## Overview

The desktop app is the **default installation experience** for EntelekX. It wraps a local web UI and a Python backend into a single installable application.

## Technology

- **Shell:** Electron (cross-platform, mature ecosystem, strong auto-updater).
- **UI:** Nuxt 4 SPA, served by the Python backend or bundled as static files.
- **Backend:** FastAPI Python process, spawned by Electron main.
- **Communication:** HTTP/WebSocket/SSE between renderer and backend.

## Process Model

```
Electron Main Process
├── Spawns Python FastAPI (http://127.0.0.1:7349)
├── Spawns optional sandbox services (Docker/Podman)
├── Auto-updater
├── Window manager
└── Loads Renderer Window
    └── Nuxt SPA (served by FastAPI or static bundle)
```

## Responsibilities of the Main Process

1. **First-run setup wizard**
   - Detect Postgres.app / Homebrew Postgres.
   - Install or configure Postgres if needed.
   - Ask for managed connection string.
   - Fallback to SQLite.
   - Generate `.env`.
2. **Database lifecycle**
   - Start/stop Postgres (if local).
   - Run Alembic migrations on startup.
3. **Backend lifecycle**
   - Start Python FastAPI as child process.
   - Monitor health; restart on crash.
   - Stop gracefully on app quit.
4. **Auto-updater**
   - Check for updates.
   - Download in background.
   - Apply on restart.
5. **Window management**
   - Open main window.
   - Handle deep links (optional).

## Single Port Convention

Default backend port: **7349**.  
If busy, increment until free. Store chosen port in `.env`.

## macOS Specifics

- Code-signed and notarised for distribution.
- Menu bar icon for quick start/stop.
- Sparkle-style updates via electron-updater.
- Postgres.app auto-detect and install helper.

## Future: Windows and Linux

- Windows installer via NSIS.
- Linux AppImage / deb / rpm.
- Shared core logic; platform-specific setup helpers.

## Related

- [[14_Installation_Experience]]
- [[15_Updates_and_Backups]]
- [[30_Decisions/ADR-003_Desktop_App_Electron]]
- [[30_Decisions/ADR-009_Electron_Backend_Spawn_Model]]
