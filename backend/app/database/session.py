from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from app.core.config import Settings, get_settings, is_production_runtime


def build_engine_options(settings: Settings) -> dict:
    """Return SQLAlchemy engine options for the configured runtime."""
    options: dict = {
        "pool_pre_ping": True,
    }

    if settings.database_url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}

        if ":memory:" in settings.database_url:
            options["poolclass"] = StaticPool

    elif settings.sqlalchemy_database_url.startswith("postgresql"):
        options["connect_args"] = {
            "prepare_threshold": None,
            "connect_timeout": 10,
        }

        if (
            is_production_runtime(settings)
            or ":6543/" in settings.sqlalchemy_database_url
        ):
            options["poolclass"] = NullPool

    return options


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """
    Build the SQLAlchemy engine lazily.

    This is important for Vercel because importing the FastAPI application
    should not require a working database connection/configuration.
    """
    settings = get_settings()

    return create_engine(
        settings.sqlalchemy_database_url,
        **build_engine_options(settings),
    )


SessionLocal = sessionmaker(
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db_session():
    db = SessionLocal(bind=get_engine())

    try:
        yield db
    finally:
        db.close()
