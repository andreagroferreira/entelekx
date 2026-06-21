# EntelekX — SPEC-008: Automatic Updates

## Status

Draft

## Scope

Define how the EntelekX desktop app and backend receive and apply updates automatically.

## Goals

- Check for updates on startup and periodically.
- Download updates in background.
- Apply on restart (or force restart for critical updates).
- Keep database migrations automatic.

## Non-Goals

- Support manual offline patching.
- Roll back updates automatically.

## Desktop App Updates

- Use `electron-updater`.
- Update server: GitHub releases with signed assets.
- Channels: stable, beta, dev.
- Apply on next restart.

## Backend Updates

- Desktop app downloads backend bundle.
- Replaces Python package directory.
- Restarts backend process.
- Runs Alembic migrations before serving.

## Headless / Docker Updates

- `entelekx update` command.
- Docker: `docker compose pull && up -d`.

## Channels

| Channel | Audience |
|---|---|
| `stable` | General users |
| `beta` | Early adopters |
| `dev` | Contributors and nightly testers |

## Security

- Updates signed with code-signing certificate.
- GitHub release assets with checksums.
- Downgrade protection (optional).

## UI Requirements

- Update available notification.
- Progress indicator for download.
- "Restart to update" button.
- Changelog viewer.

## Test Scenarios

- Update available, downloaded, applied on restart.
- Migration runs after backend update.
- Critical update forces restart.
- No update available: silent check.

## Open Questions

- How to handle DB schema downgrade if needed?
- Should users opt into beta/dev channels?

## Related

- [[../10_Architecture/15_Updates_and_Backups]]
- [[../30_Decisions/ADR-007_Automatic_Updates_Mandatory]]
