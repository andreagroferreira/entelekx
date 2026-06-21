# EntelekX — Security Model

## Trust Boundary

EntelekX is a **single-user, self-hosted AI operating system**. The primary operator is trusted. The system must prevent:

1. Unauthenticated access.
2. Accidental data loss or leakage.
3. Unintended execution of dangerous commands.
4. Exfiltration of secrets to sandboxed processes.
5. Public exposure of internal services.

## Authentication

- Local user account with bcrypt password.
- Optional TOTP 2FA.
- API tokens for external clients (IDE extension, mobile, etc.).
- Session cookies with `SameSite=Lax`, `HttpOnly`, `Secure` in production.

## Authorisation

- Single-user by default; all capabilities belong to the owner.
- Future multi-user: role-based access with Row Level Security in Postgres.
- Token scopes: `chat`, `studio`, `admin` (coarse initially, granular later).

## Code Execution Sandbox

- **Default:** Docker/Podman container per workspace.
- **Upgrade paths:** gVisor, firejail, VM-based sandbox.
- Secrets are scrubbed from subprocess environments.
- Network egress allowlist.
- Filesystem confined to workspace + temp.

## Tool Policy

- Each tool declares required capabilities.
- Destructive tools require explicit approval.
- Read/write tools confined to workspace policy.
- Browser tool isolated with URL allowlist and SSRF protection.

## SSRF and Network Safety

- Outbound URLs validated against allowlist/denylist.
- No raw requests to internal/private IPs unless explicitly allowed.
- Webhook signatures verified.

## Secrets Management

- API keys encrypted with Fernet.
- Key derived from machine fingerprint + user password.
- `.env` never committed; wizard generates it.

## Updates and Supply Chain

- Auto-updates signed and verified.
- Dependencies pinned with hashes where possible.
- CI scans for vulnerabilities (OSV, Dependabot, etc.).

## Backup and Disaster Recovery

- Automated encrypted backups.
- Restore from backup wizard.
- Export/import of projects and memories.

## Related

- [[06_Agent_Runtime]]
- [[08_Dev_Studio]]
- [[14_Installation_Experience]]
- [[15_Updates_and_Backups]]
