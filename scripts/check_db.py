from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

load_dotenv(ROOT_DIR / ".env", override=False)
load_dotenv(BACKEND_DIR / ".env", override=False)


def normalize_database_url(value: str | None) -> str:
    url = (value or "").strip()

    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]

    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]

    if url.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + url[len("postgresql+psycopg2://") :]

    return url


def redact_database_url(url: str) -> str:
    display_url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    parsed = urlsplit(display_url)

    if not parsed.hostname:
        return "configured"

    username = parsed.username or ""
    host = parsed.hostname
    port = f":{parsed.port}" if parsed.port else ""
    auth = f"{username}:***@" if username else ""

    return urlunsplit(
        (
            parsed.scheme,
            f"{auth}{host}{port}",
            parsed.path,
            parsed.query,
            parsed.fragment,
        )
    )


def main() -> None:
    raw_url = os.getenv("MIGRATION_DATABASE_URL") or os.getenv("DATABASE_URL")
    url = normalize_database_url(raw_url)

    if not url:
        raise SystemExit(
            "ERROR: MIGRATION_DATABASE_URL and DATABASE_URL are both missing. "
            "Put the real Supabase connection string in the project-root .env file "
            "or set it in the current PowerShell session."
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
        raise SystemExit(
            "ERROR: The database URL still contains a placeholder. Copy the exact "
            "connection string from Supabase Dashboard -> Connect."
        )

    print("Database URL:", redact_database_url(url))

    engine = create_engine(
        url,
        poolclass=NullPool,
        pool_pre_ping=True,
        future=True,
    )

    with engine.connect() as connection:
        identity = connection.execute(
            text("select current_database(), current_user")
        ).one()

        print("Connection: OK")
        print("Database:", identity[0])
        print("User:", identity[1])

        table_rows = connection.execute(
            text(
                "select tablename "
                "from pg_tables "
                "where schemaname = 'public' "
                "order by tablename"
            )
        ).all()

        tables = [row[0] for row in table_rows]
        print("Public tables:", ", ".join(tables) if tables else "NONE")

        if "alembic_version" in tables:
            versions = connection.execute(
                text("select version_num from alembic_version")
            ).all()
            print(
                "Alembic revision:",
                ", ".join(row[0] for row in versions) if versions else "EMPTY",
            )
        else:
            print("Alembic revision: alembic_version table is missing")

    engine.dispose()


if __name__ == "__main__":
    main()
