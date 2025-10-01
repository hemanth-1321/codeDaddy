from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv
from alembic import context
from sqlmodel import SQLModel  # make sure your models inherit from SQLModel

load_dotenv()

config = context.config

# Set DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Import all your models here so SQLModel.metadata knows about them
from db.models import *  # adjust to your path

# Set target_metadata to SQLModel.metadata
target_metadata = SQLModel.metadata  # <-- DO NOT overwrite with None

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
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
