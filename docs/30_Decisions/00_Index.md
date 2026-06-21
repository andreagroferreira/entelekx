# EntelekX — Architecture Decision Records

This section captures the key architectural decisions made during the design of EntelekX.

## ADRs

1. [[ADR-001_Stack_Python_FastAPI_Nuxt]] — why Python/FastAPI + Nuxt/Electron.
2. [[ADR-002_Data_Platform_Postgres_pgvector_sqlite_vec]] — database and vector strategy.
3. [[ADR-003_Desktop_App_Electron]] — why Electron for the desktop shell.
4. [[ADR-004_Installation_Default_Desktop_macOS]] — default installation method.
5. [[ADR-005_Smart_Database_Selector]] — how database selection works at install time.
6. [[ADR-006_First_Run_Wizard_Backup_Restore]] — backup/restore in first-run.
7. [[ADR-007_Automatic_Updates_Mandatory]] — why auto-updates are mandatory.
8. [[ADR-008_Vector_Store_Abstraction]] — why a swappable vector layer.
9. [[ADR-009_Electron_Backend_Spawn_Model]] — how Electron spawns the Python backend.

## Template

Each ADR follows the format:
- Context
- Decision
- Consequences
- Alternatives considered
- Status

## Related

- [[../10_Architecture/00_Index]]
- [[../20_Specs/00_Index]]
