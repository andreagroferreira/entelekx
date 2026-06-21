# ADR-005: Smart Database Selector

## Status

Approved

## Context

Users may already have Postgres, may want managed Postgres, or may not want to deal with databases at all. We need a graceful selection process.

## Decision

The first-run wizard uses the following order:

1. `DATABASE_URL` from existing `.env`.
2. Postgres.app on macOS.
3. Homebrew Postgres.
4. Managed Postgres provided by user (Supabase/Neon/Railway/etc.).
5. Auto-install Postgres.app (requires admin password).
6. SQLite fallback at `~/.entelekx/data/app.db`.

## Consequences

### Positive

- Most users get Postgres without manual setup.
- Power users can use managed or existing Postgres.
- No one is blocked; SQLite fallback guarantees functionality.

### Negative

- Auto-installing Postgres.app may require admin privileges and download time.
- SQLite mode is slightly degraded in concurrency.

## Alternatives Considered

- **Bundle Postgres inside the app:** increases app size and complexity.
- **Docker-only Postgres:** defeats the desktop-first goal.

## Related

- [[../10_Architecture/14_Installation_Experience]]
- [[ADR-002_Data_Platform_Postgres_pgvector_sqlite_vec]]
