# EntelekX — Initial Planning Meeting

**Date:** 2026-06-21
**Participants:** WizardingCode founder + AI assistant
**Purpose:** Define vision, stack and documentation foundation for EntelekX.

## Decisions Made

1. **Name:** EntelekX.
2. **Product type:** Personal AI operating system for founders, devs and unique-person companies.
3. **Stack:** Python/FastAPI backend, Nuxt 4 frontend, Electron desktop shell.
4. **Database:** PostgreSQL + pgvector default; SQLite + sqlite-vec fallback.
5. **Installation:** Desktop macOS app first; Docker and `curl | bash` also supported.
6. **Auto-updates:** mandatory.
7. **Backup/restore:** included in first-run wizard.
8. **License:** MIT.
9. **Repository:** `wizardingcode/entelekx`.
10. **Differentiators:** native Fusion engine, Dev Studio, Life OS, adaptive context, media forge.

## Open Questions

- Monaco vs CodeMirror for the editor?
- Should Electron backend be bundled as a standalone Python environment or installed via uv?
- Exact default Fusion preset model list?
- Which messaging channel to prioritise first after core features?

## Next Actions

- [ ] Create GitHub repository `wizardingcode/entelekx`.
- [ ] Implement Phase 0 foundation.
- [ ] Refine specs as implementation starts.

## Related

- [[../00_Index]]
- [[../01_Vision]]
- [[../40_Roadmap/00_Index]]
