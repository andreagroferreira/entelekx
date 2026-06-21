# EntelekX — Installation Experience

## Goal

A new user must be fully operational within **two minutes** of installing EntelekX.

## Supported Installation Methods

| Method | Target User | Complexity |
|---|---|---|
| macOS desktop app (.dmg) | Main target | Next-next-next wizard |
| `curl \| bash` | Power users / headless | One command |
| Docker Compose | VPS / self-hosting enthusiasts | `docker compose up -d --build` |
| Windows installer (future) | Mainstream | Next-next-next wizard |
| Linux AppImage/deb (future) | Linux users | Next-next-next wizard |

## Default Flow: macOS Desktop App

```
1. Download EntelekX.dmg
2. Drag to Applications
3. Open app
4. Welcome screen + permissions
5. Database setup wizard:
   a. Detect Postgres.app
   b. Detect Homebrew Postgres
   c. Ask for managed Postgres URL (Supabase/Neon/Railway)
   d. Offer to install Postgres.app automatically
   e. SQLite fallback with clear notice
6. Create admin account
7. Configure backup (enable/disable, location, frequency)
8. Choose default AI provider (OpenRouter recommended)
9. Paste API key or choose Ollama/local
10. Finish → open main window
```

## Smart Database Selector

The wizard tries, in order:

1. `DATABASE_URL` from existing `.env`.
2. Postgres.app on macOS.
3. Homebrew Postgres (`/usr/local/var/postgres` or `/opt/homebrew/var/postgres`).
4. Managed Postgres provided by user.
5. Auto-install Postgres.app (requires admin password).
6. SQLite fallback at `~/.entelekx/data/app.db`.

## Headless / `curl | bash`

```bash
curl -fsSL https://get.entelekx.ai | bash
```

What it does on macOS:
1. Installs Python 3.12+ if missing.
2. Installs Node.js if missing.
3. Detects/installs Postgres.app or uses managed DB.
4. Downloads latest EntelekX release.
5. Creates `~/.entelekx/` directory structure.
6. Generates `.env`, runs migrations, creates admin.
7. Starts backend and desktop app (or prints URL).

## Docker Compose

```bash
git clone https://github.com/wizardingcode/entelekx.git
cd entelekx
cp .env.example .env
docker compose up -d --build
```

Services:
- `entelekx-app`: Electron-ready backend + Nuxt static.
- `postgres`: PostgreSQL 16 + pgvector.
- (Optional) `redis`: cache and task queue.

## First-Run Backup

During setup, the wizard asks:

> "EntelekX can back up your data automatically. Where should backups go?"

Options:
- `~/.entelekx/backups` (default).
- Custom folder.
- External drive.
- Cloud sync folder (Dropbox, iCloud, etc.).
- Disabled.

Frequency: daily, weekly, manual.

## Recovery / Restore

- Menu: `Settings → Backup & Restore`.
- Choose a backup archive.
- Validate, restore DB + files, restart.

## Related

- [[13_Desktop_App_Architecture]]
- [[15_Updates_and_Backups]]
- [[30_Decisions/ADR-004_Installation_Default_Desktop_macOS]]
- [[30_Decisions/ADR-005_Smart_Database_Selector]]
- [[30_Decisions/ADR-006_First_Run_Wizard_Backup_Restore]]
