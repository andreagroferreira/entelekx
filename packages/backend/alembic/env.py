from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context
from entelekx_backend.core.config import get_settings
from entelekx_backend.models import *  # noqa: F401,F403

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = SQLModel.metadata


def get_sync_url() -> str:
    url = get_settings().resolved_database_url
    if url.startswith("sqlite+aiosqlite"):
        url = url.replace("sqlite+aiosqlite", "sqlite")
    if url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql")
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Prefer a pre-bound connection from the Alembic config (used by tests and
    the backend lifecycle). Otherwise, build a sync engine from the resolved
    DATABASE_URL.
    """
    connectable = config.attributes.get("connection")
    if connectable is None:
        sync_url = get_sync_url()
        connectable = engine_from_config(
            {"sqlalchemy.url": sync_url},
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with connectable.connect() as connection:
            _configure_and_run(connection)
    else:
        _configure_and_run(connectable)


def _configure_and_run(connection) -> None:
    ctx_kwargs = {
        "connection": connection,
        "target_metadata": target_metadata,
        "transactional_ddl": False,
        "render_as_batch": True,
    }
    context.configure(**ctx_kwargs)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
