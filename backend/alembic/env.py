import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 1. Add the backend folder to Python's path so it can find 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 2. Import ALL your models so Alembic knows what tables to create
from app.db.base import Base
# Explicitly import the new Forecast model so Alembic registers it
from app.db.models.forecast import Forecast
from app.db.models import user, resource, recommendation, anomaly

# This is the Alembic Config object
config = context.config

# 3. THE BYPASS: Hardcode the exact connection string to avoid Windows .env bugs
config.set_main_option(
    "sqlalchemy.url", 
    "postgresql://admin:supersecretpassword@127.0.0.1:5433/cloudcost"
)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Point Alembic to our models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()