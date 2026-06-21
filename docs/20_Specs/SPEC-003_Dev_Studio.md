---
type: spec
status: draft
feature: dev-studio
project: entelekx
date_created: 2026-06-21
tags: [spec, entelekx, dev, studio, code]
---

# SPEC-003: Dev Studio

## Overview

**Problem:** Existing AI agents can chat about code or run shell commands, but they are not a true development environment. EntelekX wants users to scaffold, edit, test and deploy real applications from the same workspace.

**Goal:** Implement the Dev Studio: project scaffolding, code editor, test runner, Git workflows and deployment helpers.

**Actors:**
- User (creates projects, edits code, deploys).
- Agent Kernel (delegates dev tasks).
- Dev Studio tools (scaffold, run tests, deploy).
- Sandbox (runs commands safely).

## Scope

### In scope

- Project scaffolding for 6 stacks.
- Workspace filesystem model.
- Code editor with file tree and diff view.
- Test/lint execution in sandbox.
- Git init/add/commit/push/branch UI.
- Deployment helpers for VPS, Vercel, Netlify, Fly, Railway, Render.
- AI edit application with approval.

### Out of scope

- Full IDE parity (advanced debugger, native LSP).
- All possible frameworks and deploy targets.
- CI/CD pipeline authoring in MVP.
- Live collaboration.

## Acceptance Criteria

1. **Given** a user prompt, **when** they choose "New project", **then** a scaffolded project is created for the selected stack.
2. **Given** a project, **when** the user opens a file, **then** it opens in the code editor.
3. **Given** an AI-suggested edit, **when** the user approves, **then** the file is modified and a diff is shown.
4. **Given** a project, **when** the user runs tests, **then** the sandbox executes them and streams output.
5. **Given** a project with Git configured, **when** the user commits, **then** the commit is made with AI-generated message if desired.
6. **Given** a project, **when** the user deploys to Vercel, **then** the CLI runs, returns a preview URL and logs the result.
7. **Given** the agent kernel, **when** asked to "build a landing page", **then** it can scaffold, edit and deploy via Dev Studio tools.

## Data Model

### `projects` table (extends core)

| Field | Type | Description |
|---|---|---|
| stack | str | `laravel`, `nuxt`, `vue`, `next`, `node`, `fastapi` |
| workspace_path | str | Filesystem path |
| repo_url | str | Optional remote URL |
| deploy_target | str | `vercel`, `netlify`, `vps`, `fly`, `railway`, `render` |
| deploy_config | jsonb | Tokens, env vars, SSH keys |

### `project_files` table (optional cache)

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK |
| path | str | Relative path |
| content_hash | str | Hash for diff tracking |
| last_modified | datetime | |

### `deployments` table

| Field | Type | Description |
|---|---|---|
| id | uuid | PK |
| project_id | uuid | FK |
| target | str | Deploy target |
| status | enum | `running`, `success`, `failed` |
| url | str | Live URL |
| logs | text | Deployment logs |
| created_at | datetime | |

## API Contracts

### Projects

- `POST /api/v1/projects` — create project (manual or scaffold).
- `GET /api/v1/projects` — list projects.
- `GET /api/v1/projects/{id}` — get project details.
- `PUT /api/v1/projects/{id}` — update project.
- `DELETE /api/v1/projects/{id}` — delete project.

### Files

- `GET /api/v1/projects/{id}/files?path=...` — list directory.
- `GET /api/v1/projects/{id}/files/content?path=...` — read file.
- `PUT /api/v1/projects/{id}/files/content` — write file.
- `POST /api/v1/projects/{id}/files/apply-patch` — apply AI patch.
- `GET /api/v1/projects/{id}/files/diff` — get diff for pending changes.

### Execution

- `POST /api/v1/projects/{id}/exec` — run a command in the sandbox.
- `POST /api/v1/projects/{id}/tests` — run tests.
- `POST /api/v1/projects/{id}/lint` — run linter.

### Git

- `POST /api/v1/projects/{id}/git/init` — init repo.
- `POST /api/v1/projects/{id}/git/commit` — commit.
- `POST /api/v1/projects/{id}/git/push` — push.
- `POST /api/v1/projects/{id}/git/branch` — create branch.

### Deploy

- `POST /api/v1/projects/{id}/deploy` — deploy.
- `GET /api/v1/projects/{id}/deployments` — list deployments.

## UI/UX Requirements

### Project dashboard

- Project cards with stack icon.
- "New Project" button.
- Recent activity feed.

### Project workspace

- File tree sidebar.
- Editor pane (Monaco or CodeMirror).
- Terminal panel (sandbox output).
- Git panel (status, commit, branches).
- Deploy panel (target, history, logs).

### New project wizard

- Stack selector with descriptions.
- Project name and location.
- Optional template features (auth, UI library, tests).
- Summary before create.

### AI edit flow

1. User asks agent to change something.
2. Agent proposes edits.
3. UI shows diff preview.
4. User approves/rejects each file.
5. Edits applied.

## Supported Stacks (MVP)

| Stack | Scaffolding | Test Command | Deploy Targets |
|---|---|---|---|
| Laravel | `composer create-project laravel/laravel` | `php artisan test` | VPS, Laravel Cloud |
| Vue 3 | `npm create vue@latest` | `vitest` | Vercel, Netlify, VPS |
| Nuxt 4 | `npx nuxi@latest init` | `vitest` | Vercel, Netlify, VPS |
| Next.js / React | `npx create-next-app@latest` | `jest` / `vitest` | Vercel, VPS |
| Node.js | Custom structure | `vitest` / `jest` | VPS, Railway, Render |
| Python / FastAPI | `uv` + FastAPI structure | `pytest` | VPS, Docker, Fly |

## Edge Cases

1. **Scaffolding fails (network):** retry once, show error, allow manual retry.
2. **Command runs too long:** timeout with user cancellation option.
3. **File write outside workspace:** rejected by path confinement.
4. **Deploy credentials missing:** prompt user to configure in settings.
5. **Git repo already exists:** use existing repo, do not re-init.
6. **User rejects AI edit:** keep original, offer alternative approach.
7. **Large files in editor:** lazy load or warn.

## Test Scenarios

| # | Scenario | Type | Expected |
|---|---|---|---|
| 1 | Scaffold Nuxt project | E2E | Project created with expected files |
| 2 | Open and edit file | E2E | Changes saved, diff shown |
| 3 | Run tests | Integration | Test output streamed, summary parsed |
| 4 | Apply AI patch | Integration | File modified after approval |
| 5 | Commit via UI | Integration | Commit created with message |
| 6 | Deploy to Vercel | Integration | Preview URL returned |
| 7 | Path confinement rejects escape | Security | Write rejected |
| 8 | Sandbox command timeout | Integration | Timeout error, process killed |

## Dependencies

- [ ] SPEC-001 Agent Kernel.
- [ ] Sandbox runtime (Docker/Podman).
- [ ] Monaco or CodeMirror editor.
- [ ] Git binary available in sandbox/host.
- [ ] Deployment CLI tokens encrypted storage.

## Open Questions

- Monaco vs CodeMirror for the editor?
- Should LSP be proxied from backend or omitted in MVP?
- Should deployment run in user's local CLI context or always in sandbox?

## Related

- [[10_Architecture/08_Dev_Studio]]
- [[40_Roadmap/Phase_3_Dev_Studio]]
- [[50_Research/Open_Design_Analysis]]
