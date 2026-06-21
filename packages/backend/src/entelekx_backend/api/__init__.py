"""API routers."""

import asyncio
from pathlib import Path

import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import select

from entelekx_backend.api.chat import chat_router
from entelekx_backend.core.config import get_settings
from entelekx_backend.db.backend import get_database_backend
from entelekx_backend.models import ProviderConfig, User

__all__ = ["chat_router", "health_router", "setup_router"]

health_router = APIRouter(tags=["health"])
setup_router = APIRouter(tags=["setup"])


@health_router.get("/health")
async def health():
    backend = get_database_backend()
    db_ok = await backend.health_check()
    await backend.disconnect()
    return {
        "status": "ok" if db_ok else "degraded",
        "version": get_settings().version,
        "database": "connected" if db_ok else "unreachable",
    }


class DatabaseValidationRequest(BaseModel):
    url: str = Field(..., description="Database connection string")


class DatabaseValidationResponse(BaseModel):
    valid: bool
    backend: str
    message: str


@setup_router.post("/validate-database", response_model=DatabaseValidationResponse)
async def validate_database(req: DatabaseValidationRequest):
    backend_type = (
        "postgres"
        if req.url.startswith("postgresql")
        else "sqlite"
        if req.url.startswith("sqlite")
        else "unknown"
    )
    try:
        backend = get_database_backend(req.url)
        ok = await backend.connect() or await backend.health_check()
        await backend.disconnect()
        return DatabaseValidationResponse(
            valid=ok,
            backend=backend_type,
            message="Connection successful" if ok else "Could not connect",
        )
    except Exception as exc:
        return DatabaseValidationResponse(
            valid=False,
            backend=backend_type,
            message=f"Validation failed: {exc}",
        )


class SetupInitializeRequest(BaseModel):
    database_url: str | None = None
    admin_username: str
    admin_password: str
    backup_enabled: bool = True
    backup_path: str | None = None
    backup_frequency: str = "daily"
    backup_encrypted: bool = True
    default_provider: str = "openrouter"
    openrouter_api_key: str | None = None
    ollama_base_url: str | None = None


class SetupInitializeResponse(BaseModel):
    status: str
    database_backend: str
    admin_username: str
    backup_enabled: bool


def _derive_backend(url: str | None) -> str:
    if url and url.startswith("postgresql"):
        return "postgres"
    return "sqlite"


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _write_env_file(settings_path: Path, values: dict[str, str]) -> None:
    lines: list[str] = []
    if settings_path.exists():
        existing = settings_path.read_text(encoding="utf-8").splitlines()
        keys_seen: set[str] = set()
        for line in existing:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key = stripped.split("=", 1)[0]
                if key in values:
                    lines.append(f"{key}={values[key]}")
                    keys_seen.add(key)
                    continue
            lines.append(line)
        for key, value in values.items():
            if key not in keys_seen:
                lines.append(f"{key}={value}")
    else:
        lines.append("# EntelekX environment configuration")
        for key, value in values.items():
            lines.append(f"{key}={value}")
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _test_backup_location(path_str: str) -> bool:
    try:
        path = Path(path_str).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".entelekx_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


@setup_router.post("/initialize", response_model=SetupInitializeResponse)
async def initialize(req: SetupInitializeRequest):
    settings = get_settings()
    database_url = req.database_url or settings.resolved_database_url
    backend = get_database_backend(database_url)

    try:
        await backend.connect()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Database connection failed: {exc}") from exc

    async with backend.session() as session:
        existing = await session.execute(select(User).where(User.username == req.admin_username))
        if existing.scalars().first() is None:
            user = User(
                username=req.admin_username,
                password_hash=_hash_password(req.admin_password),
            )
            session.add(user)

        provider = await session.execute(
            select(ProviderConfig).where(ProviderConfig.provider == req.default_provider)
        )
        if provider.scalars().first() is None:
            key = req.openrouter_api_key or ""
            config = ProviderConfig(
                provider=req.default_provider,
                encrypted_key=key,
                settings={"ollama_base_url": req.ollama_base_url} if req.ollama_base_url else {},
            )
            session.add(config)

    backup_path = req.backup_path or str(settings.data_dir / "backups")
    backup_ok = await asyncio.to_thread(_test_backup_location, backup_path)
    if not backup_ok:
        await backend.disconnect()
        raise HTTPException(status_code=400, detail=f"Backup path is not writable: {backup_path}")

    env_path = settings.data_dir / ".env"
    env_values = {
        "DATABASE_URL": database_url,
        "DATABASE_BACKEND": _derive_backend(database_url),
        "BACKUP_ENABLED": "true" if req.backup_enabled else "false",
        "BACKUP_PATH": backup_path,
        "BACKUP_FREQUENCY": req.backup_frequency,
        "BACKUP_ENCRYPTED": "true" if req.backup_encrypted else "false",
        "DEFAULT_PROVIDER": req.default_provider,
        "OPENROUTER_API_KEY": req.openrouter_api_key or "",
        "OLLAMA_BASE_URL": req.ollama_base_url or "",
        "ADMIN_USERNAME": req.admin_username,
    }
    await asyncio.to_thread(_write_env_file, env_path, env_values)

    await backend.disconnect()
    return SetupInitializeResponse(
        status="initialized",
        database_backend=backend.__class__.__name__,
        admin_username=req.admin_username,
        backup_enabled=req.backup_enabled,
    )


class BackupRequest(BaseModel):
    path: str | None = None
    encrypted: bool = True


class BackupResponse(BaseModel):
    success: bool
    archive_path: str | None
    message: str


@setup_router.post("/backup", response_model=BackupResponse)
async def backup(req: BackupRequest):
    settings = get_settings()
    backup_path = req.path or str(settings.data_dir / "backups")
    ok = await asyncio.to_thread(_test_backup_location, backup_path)
    if not ok:
        return BackupResponse(
            success=False,
            archive_path=None,
            message=f"Backup path is not writable: {backup_path}",
        )
    return BackupResponse(
        success=True,
        archive_path=str(Path(backup_path) / "entelekx_backup_test.zip"),
        message="Backup location verified",
    )
