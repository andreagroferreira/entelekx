---
type: spec
status: draft
feature: backup-restore
project: entelekx
date_created: 2026-06-21
tags: [spec, entelekx, backup, restore, data]
---

# SPEC-009: First-Run Backup and Restore

## Overview

**Problem:** EntelekX stores valuable personal and business data. Losing it would be catastrophic. Backup must be offered during setup and easy to restore.

**Goal:** Provide automatic local backups of database + files, with optional encryption, configurable from the first-run wizard and the settings page.

**Actors:**
- End user (configures and restores backups).
- Scheduler (triggers backups).
- Backup worker (creates archives).
- Restore worker (recovers data).

## Scope

### In scope

- Backup scheduler.
- Backup archive creation (DB + files).
- Optional AES-256 encryption.
- Restore from archive.
- UI in wizard and settings.
- Retention policy.

### Out of scope

- Cloud backup service (user may sync folder to Dropbox/iCloud themselves).
- Real-time replication.
- Incremental backups in MVP (full archives).

## Acceptance Criteria

1. **Given** the first-run wizard, **when** the user enables backups, **then** a test backup runs and succeeds.
2. **Given** daily backups enabled, **when** the scheduled time passes, **then** a new archive is created.
3. **Given** an encrypted backup, **when** restore runs with the correct password, **then** all data is recovered.
4. **Given** an encrypted backup, **when** restore runs with the wrong password, **then** it fails with a clear error.
5. **Given** a backup archive, **when** the user restores it, **then** current data is replaced and the backend restarts.
6. **Given** retention settings, **when** old backups exceed the limit, **then** oldest archives are deleted.

## Data Model

### `backups` table

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| path | str | Archive file path |
| size_bytes | int | Archive size |
| backend | str | `postgres` or `sqlite` |
| encrypted | bool | AES-256 encryption |
| status | str | `success`, `failed`, `in_progress` |
| started_at | datetime | Start time |
| completed_at | datetime | End time |
| error | str | Error message if failed |

## API Contracts

### HTTP

- `POST /api/backups/run` — trigger a manual backup.
- `GET /api/backups` — list backups.
- `POST /api/backups/restore` — restore from a backup file.
- `DELETE /api/backups/{id}` — delete a backup archive.
- `GET /api/backups/settings` — get backup settings.
- `PUT /api/backups/settings` — update backup settings.

## UI/UX Requirements

### Settings page

- Toggle "Enable automatic backups".
- Backup location input with folder picker.
- Frequency selector: daily, weekly, monthly, manual.
- Retention inputs: keep last N daily / weekly / monthly.
- Encryption toggle + password input.
- "Backup now" button.
- List of backups with size, date, status, restore/delete actions.
- "Restore from backup" button.

### Restore dialog

- File picker.
- Password input if encrypted.
- Warning: current data will be overwritten.
- Progress bar for restore.
- Restart confirmation.

## Edge Cases

1. **Backup disk full:** fail gracefully, notify user, do not delete existing backups.
2. **Backup in progress when another starts:** queue or skip.
3. **Restore with mismatched app version:** warn and block or allow with migration.
4. **Backup archive corrupted:** validate before restore and show error.
5. **Postgres restore while app running:** stop backend, restore, restart.
6. **SQLite restore while app running:** stop backend, replace file, restart.

## Test Scenarios

| # | Scenario | Type | Expected |
|---|---|---|---|
| 1 | Trigger manual backup | Integration | Archive created with DB + files |
| 2 | Scheduled backup fires | Integration | Archive appears at scheduled time |
| 3 | Restore backup | Integration | Data recovered, backend restarts |
| 4 | Encrypted backup restore | Integration | Data recovered with correct password |
| 5 | Wrong password fails | Unit | Clear error, no data change |
| 6 | Retention deletes old backups | Unit | Only N most recent remain |
| 7 | Corrupted archive validation | Unit | Restore rejected before applying |

## Dependencies

- [ ] Database abstraction (SPEC-006).
- [ ] Encryption key derivation.
- [ ] Filesystem access from backend.

## Open Questions

- Should backups include the entire `~/.entelekx` directory or exclude logs/cache?
- Should we support incremental backups later?

## Related

- [[SPEC-005_Installation_Wizard]]
- [[10_Architecture/15_Updates_and_Backups]]
- [[30_Decisions/ADR-006_First_Run_Wizard_Backup_Restore]]
