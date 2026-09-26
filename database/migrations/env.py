from __future__ import annotations

import importlib
import os
import sys
from logging.config import fileConfig
from pathlib import Path
from typing import Any

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(ROOT_DIR / ".env", override=False)
load_dotenv(BACKEND_DIR / ".env", override=False)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def normalize_database_url(value: str | None) -> str:
    url = (value or "").strip()

    if not url:
        return ""

    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]

    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]

    if url.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + url[len("postgresql+psycopg2://") :]

    return url


def _settings_database_url() -> str:
    try:
        from app.core.config import get_settings

        settings = get_settings()
        migration_url = getattr(settings, "migration_database_url", None)
        database_url = getattr(settings, "database_url", None)
        return str(migration_url or database_url or "").strip()
    except Exception:
        return ""


def get_migration_database_url() -> str:
    raw_url = (
        os.getenv("MIGRATION_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or _settings_database_url()
    )

    url = normalize_database_url(raw_url)

    if not url:
        raise RuntimeError(
            "No database URL is configured. Set MIGRATION_DATABASE_URL in the "
            "current shell or in the project-root .env file."
        )

    placeholders = (
        "YOUR_PROJECT_REF",
        "PROJECT_REF",
        "POOLER_HOST",
        "YOUR-PASSWORD",
        "[YOUR-PASSWORD]",
        "[PROJECT-REF]",
    )

    if any(token in url for token in placeholders):
        raise RuntimeError(
            "MIGRATION_DATABASE_URL still contains a placeholder. Copy the exact "
            "Session pooler or Direct connection string from Supabase -> Connect."
        )

    return url


def _load_target_metadata() -> Any:
    candidates = (
        ("app.database.base", "Base"),
        ("app.database.models", "Base"),
        ("app.models", "Base"),
    )

    for module_name, attribute_name in candidates:
        try:
            module = importlib.import_module(module_name)
            base = getattr(module, attribute_name, None)
            metadata = getattr(base, "metadata", None)
            if metadata is not None:
                return metadata
        except Exception:
            continue

    return None


target_metadata = _load_target_metadata()
database_url = get_migration_database_url()

config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
