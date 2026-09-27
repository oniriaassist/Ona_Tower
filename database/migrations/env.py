import os
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import pool
from sqlalchemy import text

from alembic import context

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings, normalize_database_url
from app.database.base import Base
from app.database import models


# Alembic Config object
config = context.config

# Load the runtime database URL, with an optional migration-only override.
settings = get_settings()
database_url = normalize_database_url(os.environ.get("MIGRATION_DATABASE_URL") or settings.database_url)
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"),)

# Configure Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata used by Alembic for autogenerate
target_metadata = Base.metadata
INITIAL_REVISION = "05b4c32881e1"
HEAD_REVISION = "c4f2a31b7d90"
INITIAL_TABLES = {
    "amenities",
    "enquiries",
    "floor_plans",
    "location_points",
    "residence_media",
    "residences",
    "smart_features",
}
ADMIN_TABLES = {"admin_settings", "admin_team_members"}
ADMIN_ENQUIRY_COLUMNS = {"assigned_to", "internal_notes", "updated_at"}
ADMIN_ACCOUNT_COLUMNS = {"department", "password_hash", "is_super_admin", "last_login_at", "password_reset_requested_at"}


def stamp_existing_sqlite_schema(connection) -> None:
    """Mark legacy local SQLite schemas that were created before Alembic.

    Earlier local setup could create tables via SQLAlchemy bootstrap without
    writing an Alembic version. Running `alembic upgrade head` against that
    database should preserve data and continue from the matching revision.
    """
    if connection.dialect.name != "sqlite":
        return

    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if not INITIAL_TABLES.issubset(tables):
        return

    connection.execute(
        text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)")
    )
    existing_version = connection.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar()

    enquiry_columns = {column["name"] for column in inspector.get_columns("enquiries")}
    admin_columns = (
        {column["name"] for column in inspector.get_columns("admin_team_members")}
        if "admin_team_members" in tables
        else set()
    )

    if (
        ADMIN_TABLES.issubset(tables)
        and ADMIN_ENQUIRY_COLUMNS.issubset(enquiry_columns)
        and ADMIN_ACCOUNT_COLUMNS.issubset(admin_columns)
        and "site_visits" in tables
    ):
        detected_revision = HEAD_REVISION
    elif ADMIN_TABLES.issubset(tables) and ADMIN_ENQUIRY_COLUMNS.issubset(enquiry_columns):
        detected_revision = "9b6a7f0f3e12"
    else:
        detected_revision = INITIAL_REVISION

    if not existing_version:
        connection.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:revision)"),
            {"revision": detected_revision},
        )
    elif existing_version == "9b6a7f0f3e12" and detected_revision == HEAD_REVISION:
        # A prior development bootstrap may already have created the head
        # columns/tables while Alembic still records the previous revision.
        # Align the version marker with the schema rather than replaying
        # additive DDL and raising duplicate-column errors.
        connection.execute(
            text("UPDATE alembic_version SET version_num = :revision"),
            {"revision": HEAD_REVISION},
        )
    elif existing_version == INITIAL_REVISION and detected_revision in {"9b6a7f0f3e12", HEAD_REVISION}:
        connection.execute(
            text("UPDATE alembic_version SET version_num = :revision"),
            {"revision": detected_revision},
        )
    connection.commit()


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    engine_kwargs = {"poolclass": pool.NullPool}
    if database_url.startswith(("postgresql", "postgres")):
        engine_kwargs["connect_args"] = {"prepare_threshold": None}

    connectable = create_engine(database_url, **engine_kwargs)

    with connectable.connect() as connection:
        stamp_existing_sqlite_schema(connection)
        # SQLAlchemy 2.x inspections can autobegin a transaction. Close that
        # transaction before handing control to Alembic so migration/version
        # changes are committed reliably, especially on SQLite.
        connection.commit()
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
