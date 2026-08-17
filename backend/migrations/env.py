"""Alembic migration environment.

Both the URL and the target metadata are wired to the app rather than to
alembic.ini: the database URL comes from ``Settings.database_url``, and
``target_metadata`` is ``SQLModel.metadata`` populated by importing ``app.models``.

    uv run alembic upgrade head                              # apply migrations
    uv run alembic revision --autogenerate -m "<message>"   # create a migration
    uv run alembic upgrade head --sql                        # render SQL, no DB needed
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

import app.models  # noqa: F401 — registers every table on SQLModel.metadata
from app.core.config import get_settings

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
