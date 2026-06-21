# EntelekX — Dev Studio

## Goal

Turn EntelekX into a first-class environment for building real applications. Not just code chat, but scaffolding, editing, testing, versioning and deployment.

## Supported Stacks (MVP)

| Stack | Scaffolding Tool | Test Command | Deploy Targets |
|---|---|---|---|
| Laravel | Composer + Laravel installer | `php artisan test` | VPS, Laravel Cloud, Forge |
| Vue 3 | npm + Vite | `npm run test:unit` | VPS, Vercel, Netlify |
| Nuxt 4 | `nuxi init` / `nuxi@latest` | `vitest` | VPS, Vercel, Netlify |
| Next.js / React | `create-next-app` | `jest` / `vitest` | Vercel, VPS |
| Node.js | npm + structure | `vitest` / `jest` | VPS, Railway, Render |
| Python / FastAPI | `uv` + FastAPI structure | `pytest` | VPS, Docker, Fly |

## Capabilities

### Scaffolding

- Generate project from prompt or template.
- Choose stack, name, folder, initial features.
- Create `.env`, README, CI starter.

### Code Editing

- File tree explorer in the UI.
- Monaco editor (VS Code editor component) or CodeMirror.
- Apply AI-generated edits as patches or full rewrites.
- Diff preview before applying.

### Execution

- Run tests, lint, typecheck inside sandbox.
- Show output stream in UI.
- Capture exit codes and parse results.

### Git Integration

- `git init`, `git add`, `git commit`, `git push`.
- Branch creation from UI.
- Diff view.
- PR draft generation.

### Deployment

- Build Docker image.
- Deploy to VPS via SSH.
- Deploy to Vercel / Netlify via CLI tokens.
- Deploy to Fly / Railway via CLI tokens.
- Preview URL returned to chat.

### Design Handoff

- Generate `DESIGN.md` from brief or screenshot (inspired by Open Design).
- Apply design system to existing project via code migration.
- Preview UI artefacts before exporting to repo.

## Workspace Model

Each project in EntelekX has an associated filesystem workspace. Tools are confined to that workspace plus a shared temp directory.

## Security

- All code execution runs inside Docker/Podman by default.
- Network egress allowlist per workspace.
- Secrets (.env, API keys) are never exposed to sandboxed processes.
- Destructive operations require approval.

## Related

- [[06_Agent_Runtime]]
- [[10_Media_Forge]]
- [[12_Security_Model]]
- [[50_Research/Open_Design_Analysis]]
- [[20_Specs/SPEC-003_Dev_Studio]]
