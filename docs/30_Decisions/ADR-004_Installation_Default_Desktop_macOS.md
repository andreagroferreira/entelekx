# ADR-004: Installation Default — Desktop macOS App

## Status

Approved

## Context

EntelekX wants to be installed and running in two minutes. Docker is a good deployment option but not the friendliest first-run experience for non-technical users.

## Decision

The **default installation method** is the **macOS desktop app** distributed as a `.dmg` installer with a setup wizard.

## Consequences

### Positive

- Best UX for the target user (founders, builders).
- Hides Postgres setup, migrations and backend startup.
- Enables auto-updates and native OS integration.

### Negative

- Requires code signing and notarisation for macOS distribution.
- Linux and Windows come later.

## Alternatives Considered

- **Docker-first:** easier for us, harder for average users.
- **Web-only:** cannot manage local backend lifecycle.

## Related

- [[../10_Architecture/14_Installation_Experience]]
- [[SPEC-005_Installation_Wizard]]
