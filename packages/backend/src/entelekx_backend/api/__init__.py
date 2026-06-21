"""API routers."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from entelekx_backend.core.config import get_settings
from entelekx_backend.db.backend import get_database_backend

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
    try:
        backend = get_database_backend(req.url)
        ok = await backend.health_check()
        await backend.disconnect()
        backend_type = "postgres" if req.url.startswith("postgresql") else "sqlite"
        return DatabaseValidationResponse(
            valid=ok,
            backend=backend_type,
            message="Connection successful" if ok else "Could not connect",
        )
    except Exception as exc:
        return DatabaseValidationResponse(
            valid=False,
            backend="unknown",
            message=f"Validation failed: {exc}",
        )


class SetupInitializeRequest(BaseModel):
    database_url: str | None = None
    admin_username: str
    admin_password: str
    backup_enabled: bool = True
    backup_path: str | None = None
    default_provider: str = "openrouter"
    openrouter_api_key: str | None = None


@setup_router.post("/initialize")
async def initialize(req: SetupInitializeRequest):
    # Phase 0 stub: just validate DB and return success.
    # Real admin creation and migrations will be added in Phase 1.
    backend = get_database_backend(req.database_url)
    ok = await backend.health_check()
    await backend.disconnect()
    if not ok:
        raise HTTPException(status_code=400, detail="Database connection failed")
    return {"status": "initialized", "database_backend": backend.__class__.__name__}
