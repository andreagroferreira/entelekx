"""EntelekX backend application entrypoint."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv(encoding="utf-8-sig")

from entelekx_backend.api import health_router, setup_router
from entelekx_backend.core.config import Settings, get_settings

settings = get_settings()

app = FastAPI(
    title="EntelekX",
    description="Personal AI operating system backend",
    version=settings.version,
)

# CORS for local desktop/web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7349", "http://127.0.0.1:7349"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(setup_router, prefix="/api/v1/setup")

# Serve the bundled Nuxt SPA from a relative static directory if present.
_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_STATIC_DIR):
    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")


@app.on_event("startup")
async def startup():
    """Validate database connectivity on startup."""
    from entelekx_backend.db.backend import get_database_backend

    backend = get_database_backend(settings.database_url)
    await backend.connect()
    await backend.health_check()
    await backend.disconnect()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=settings.port)
