---
type: spec
status: draft
feature: installation-wizard
project: entelekx
date_created: 2026-06-21
tags: [spec, entelekx, installation, desktop, foundation]
---

# SPEC-005: Installation Wizard

## Overview

**Problem:** EntelekX targets solo founders, developers and non-technical builders. They need to be operational in 2 minutes, without manually configuring PostgreSQL, Python or the backend.

**Goal:** Provide a first-run wizard in the Electron desktop app that detects, installs or configures a database, sets up the default AI provider, configures backups and opens the main window.

**Actors:**
- End user installing EntelekX on macOS.
- Electron main process (spawns helpers).
- Database setup helper (shell scripts + AppleScript/CLI).
- Backend process.

## Scope

### In scope

- Welcome screen.
- macOS permissions helper.
- Smart database selector:
  - Detect Postgres.app.
  - Detect Homebrew Postgres.
  - Accept managed Postgres URL (Supabase/Neon/Railway/etc.).
  - Auto-install Postgres.app (with admin password prompt).
  - SQLite fallback.
- Admin account creation.
- Backup configuration.
- AI provider setup (OpenRouter default, Ollama/local option).
- Final summary + open main window.

### Out of scope

- Windows and Linux wizard details (future specs).
- Complex database migration from other tools.
- Cloud SSO login.
- In-app purchase.

## Acceptance Criteria

1. **Given** a fresh macOS install, **when** the user opens EntelekX, **then** the wizard starts automatically.
2. **Given** Postgres.app already installed, **when** the wizard runs, **then** it detects and uses it without asking.
3. **Given** no Postgres available, **when** the user chooses managed DB, **then** the wizard validates the connection string.
4. **Given** no Postgres and no managed DB, **when** the user agrees, **then** the wizard downloads and installs Postgres.app automatically.
5. **Given** the user declines all Postgres options, **when** the wizard finishes, **then** SQLite fallback is active and functional.
6. **Given** the wizard completes, **when** the user clicks finish, **then** the backend starts and the main window opens within 10 seconds.
7. **Given** the wizard completes, **when** the app restarts, **then** it skips the wizard and loads the main window.

## Data Model

### Stored configuration (`.env` / settings)

| Field | Example | Source |
|---|---|---|
| `DATABASE_URL` | `postgresql://...` or `sqlite+aiosqlite://...` | Wizard |
| `DATABASE_BACKEND` | `postgres` / `sqlite` | Derived |
| `BACKUP_ENABLED` | `true` | Wizard |
| `BACKUP_PATH` | `~/.entelekx/backups` | Wizard |
| `BACKUP_FREQUENCY` | `daily` | Wizard |
| `BACKUP_ENCRYPTED` | `true` | Wizard |
| `DEFAULT_PROVIDER` | `openrouter` | Wizard |
| `OPENROUTER_API_KEY` | `sk-...` | Wizard |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Wizard (optional) |
| `ADMIN_USERNAME` | `founder` | Wizard |

## API Contracts

### Internal (Electron → backend)

- `POST /api/setup/validate-database` — validate connection string.
- `POST /api/setup/initialize` — run migrations, create admin.
- `POST /api/setup/backup` — trigger test backup.

### HTTP (backend)

- `GET /api/health` — backend and DB healthy.

## UI/UX Requirements

### Wizard steps (maximum 6)

1. **Welcome** — logo, one-line promise, CTA.
2. **Database** — smart selector UI:
   - Detected options listed with radio buttons.
   - "Use managed Postgres" button reveals URL input.
   - "Install Postgres.app" button triggers download/install.
   - "Use SQLite" as last resort with clear notice.
3. **Admin Account** — username, password, password confirmation.
4. **Backup** — location, frequency, encryption toggle, test backup button.
5. **AI Provider** — OpenRouter default; key input with test button; Ollama/local toggle.
6. **Summary** — show config overview; finish button.

### States

- Loading spinner during detection/installation.
- Inline validation errors.
- "Back" and "Next" buttons disabled until current step valid.
- Progress dots at top.

## Edge Cases

1. **Postgres.app download fails:** show error, offer manual download link and SQLite fallback.
2. **Managed Postgres URL invalid:** show connection error details.
3. **API key test fails:** allow continue and configure later.
4. **Backup location not writable:** suggest default and retry.
5. **Backend fails to start after wizard:** show logs and restart button.
6. **Wizard interrupted mid-setup:** on restart, resume or clean up partial state.

## Test Scenarios

| # | Scenario | Type | Expected |
|---|---|---|---|
| 1 | Detect Postgres.app automatically | E2E | Database step pre-selected |
| 2 | Install Postgres.app via wizard | E2E | App downloads, installs, DB created |
| 3 | Use managed Postgres URL | Integration | Connection validated, migrations run |
| 4 | SQLite fallback end-to-end | E2E | App functional with SQLite |
| 5 | Wizard skips on second launch | E2E | Main window opens directly |
| 6 | Invalid API key allows continue | E2E | User lands on dashboard, can configure later |
| 7 | Test backup succeeds | Integration | Backup archive created |
| 8 | Backend health check after setup | Unit | Returns healthy |

## Dependencies

- [ ] SPEC-006 Database Abstraction.
- [ ] SPEC-009 First-Run Backup and Restore.
- [ ] Electron main process spawn model (ADR-009).
- [ ] macOS code signing for auto-install helpers.
- [ ] Postgres.app download URL stable.

## Open Questions

- Should the wizard auto-install Postgres.app silently with admin prompt, or open the installer and wait?
- Should we bundle Postgres inside the app to avoid downloads?

## Related

- [[SPEC-006_Database_Abstraction]]
- [[SPEC-009_First_Run_Backup_Restore]]
- [[10_Architecture/14_Installation_Experience]]
- [[30_Decisions/ADR-004_Installation_Default_Desktop_macOS]]
- [[30_Decisions/ADR-005_Smart_Database_Selector]]
- [[30_Decisions/ADR-006_First_Run_Wizard_Backup_Restore]]
