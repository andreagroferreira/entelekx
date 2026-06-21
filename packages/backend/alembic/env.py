from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from entelekx_backend.core.config import get_settings
from entelekx_backend.db.backend import get_database_backend

# Import all models so Alembic can autogenerate
# from entelekx_backend.models import *

target_metadata = SQLModel.metadata


def run_migrations_offline():
    url = get_settings().resolved_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    backend = get_database_backend(get_settings().resolved_database_url)
    # Use sync engine for Alembic
    sync_url = get_settings().resolved_database_url
    if sync_url.startswith("sqlite+aiosqlite"):
        sync_url = sync_url.replace("sqlite+aiosqlite", "sqlite")
    connectable = engine_from_config(
        {"sqlalchemy.url": sync_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    backend.disconnect()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
