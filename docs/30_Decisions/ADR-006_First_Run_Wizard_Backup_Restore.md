# ADR-006: First-Run Wizard — Backup and Restore

## Status

Approved

## Context

EntelekX stores valuable user data: projects, memories, decisions, generated artefacts. Data loss would be catastrophic. Backup must be discoverable from day one.

## Decision

The first-run wizard must include a backup configuration step:
- Choose backup location (default `~/.entelekx/backups`).
- Choose frequency (daily/weekly/monthly/manual).
- Optionally encrypt backups.
- Perform a test backup.

Restore is available at any time via Settings.

## Consequences

### Positive

- Users protect their data from the start.
- Backups are local and under user control.
- Recovery path is clear.

### Negative

- Adds one step to first-run wizard.
- Backup storage uses disk space.

## Alternatives Considered

- **Cloud backup service:** contradicts self-hosted sovereignty.
- **No first-run backup:** users might never configure it.

## Related

- [[../10_Architecture/15_Updates_and_Backups]]
- [[SPEC-005_Installation_Wizard]]
- [[SPEC-009_First_Run_Backup_Restore]]
