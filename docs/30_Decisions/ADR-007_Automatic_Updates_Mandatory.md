# ADR-007: Automatic Updates Mandatory

## Status

Approved

## Context

EntelekX ships frequently and handles security-critical functions (code execution, secrets, external APIs). Users may not update manually.

## Decision

Automatic updates are **mandatory** by default. The desktop app checks for updates on startup, downloads them in the background and applies on restart. Critical updates can force a restart.

## Consequences

### Positive

- Security patches reach users quickly.
- Migrations run automatically.
- Reduces support burden from outdated versions.

### Negative

- Some users may object to auto-updates.
- Requires signed releases and robust update server.

## Mitigations

- Allow opt-out for advanced users (with clear warning).
- Show changelog before applying.
- Provide beta/dev channels.

## Alternatives Considered

- **Manual updates only:** safer for autonomy but risks stale installs.

## Related

- [[../10_Architecture/15_Updates_and_Backups]]
- [[SPEC-008_Automatic_Updates]]
