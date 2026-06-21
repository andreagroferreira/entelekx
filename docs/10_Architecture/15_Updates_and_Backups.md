# EntelekX — Updates and Backups

## Automatic Updates (Mandatory)

### Desktop App

- `electron-updater` checks for updates on startup and periodically.
- If an update is available:
  - Download in background.
  - Notify user.
  - Apply on next restart (or force restart for critical updates).
- Updates must be signed with the project's code-signing certificate.

### Backend

- The backend exposes `/api/version` and `/api/update/check`.
- If a newer release is available, the desktop app downloads it.
- Backend update is applied by replacing the Python package directory and restarting the child process.
- Migrations run automatically on next startup.

### Headless / Docker

- `curl | bash` installs the latest release and can self-update via `entelekx update`.
- Docker mode: `docker compose pull && docker compose up -d`.

## Backup Strategy

### What to Back Up

| Data | Location | Backup Method |
|---|---|---|
| PostgreSQL database | Postgres server | `pg_dump` |
| SQLite database | `~/.entelekx/data/app.db` | File copy |
| Vector stores | Same DB or filesystem | Included in DB backup |
| Generated artefacts | `~/.entelekx/artefacts/` | File archive |
| Configuration | `~/.entelekx/.env`, settings | Encrypted archive |
| User uploads | `~/.entelekx/uploads/` | File archive |

### Backup Format

- Each backup is a timestamped `.zip` or `.tar.gz`.
- Metadata JSON inside: version, timestamp, backend type, size.
- Optional AES-256 encryption with user password.

### Backup Scheduler

| Frequency | Default | Notes |
|---|---|---|
| Daily | ✅ recommended | Keep last 7 days |
| Weekly | optional | Keep last 4 weeks |
| Monthly | optional | Keep last 12 months |
| Manual | always available | One-click |

### Retention

- Local retention policy configurable.
- Default: 7 daily, 4 weekly, 12 monthly.

## Restore

1. User selects backup file in UI.
2. System validates format and version compatibility.
3. Warns about overwriting current data.
4. Restores database via `pg_restore` or file replacement.
5. Restores files to original paths.
6. Restarts backend.
7. Re-indexes vector store if needed.

## Disaster Recovery Notes

- Backups should be stored outside the EntelekX data directory.
- Encourage users to sync backup folder to cloud or external drive.
- Provide "Export all data" for migration.

## Related

- [[13_Desktop_App_Architecture]]
- [[14_Installation_Experience]]
- [[30_Decisions/ADR-006_First_Run_Wizard_Backup_Restore]]
- [[30_Decisions/ADR-007_Automatic_Updates_Mandatory]]
