"""Core configuration and settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EntelekX"
    version: str = "0.1.0"
    port: int = 7349
    host: str = "127.0.0.1"

    data_dir: Path = Path.home() / ".entelekx"

    database_url: str | None = None

    openrouter_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    log_level: str = "INFO"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        # Fallback to SQLite in data directory
        db_path = self.data_dir / "data" / "app.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite+aiosqlite:///{db_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
