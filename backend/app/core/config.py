from functools import lru_cache
from pathlib import Path
from typing import Literal
import json
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


def normalize_database_url(url: str) -> str:
    """Normalize database URLs for consistent local and production behavior."""
    if url.startswith("sqlite+pysqlite:///./"):
        relative_path = url[len("sqlite+pysqlite:///./"):]
        return f"sqlite+pysqlite:///{(PROJECT_ROOT / relative_path).resolve().as_posix()}"
    if url.startswith("sqlite:///./"):
        relative_path = url[len("sqlite:///./"):]
        return f"sqlite+pysqlite:///{(PROJECT_ROOT / relative_path).resolve().as_posix()}"
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Settings(BaseSettings):
    app_name: str = "ONA Towers API"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_debug: bool = True
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8400
    # Kept as a string so .env accepts both comma-separated and JSON-array values.
    cors_origins: str = "http://localhost:3010,http://127.0.0.1:3010"
    cors_origin_regex: str | None = None
    log_level: str = "INFO"

    database_url: str = "sqlite+pysqlite:///./database/ona_towers.db"
    auto_init_db: bool = False

    enquiry_rate_limit_count: int = 5
    enquiry_rate_limit_window_seconds: int = 3600
    duplicate_enquiry_window_seconds: int = 120
    max_message_length: int = 2000

    smtp_enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = "ONA Towers"
    smtp_use_tls: bool = True
    sales_notification_email: str | None = None

    # The first database-backed administrator is bootstrapped from these values.
    admin_email: str = "admin@onatowers.dev"
    admin_password: str = "ona-admin-local"
    admin_name: str = "ONA Administrator"
    admin_role: str = "Administrator"
    admin_department: str = "Administration"
    admin_session_secret: str = "ona-local-development-secret"
    admin_session_hours: int = 12

    model_config = SettingsConfigDict(
        env_file=(str(PROJECT_ROOT / ".env"), str(BACKEND_DIR / ".env")),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        value = self.cors_origins.strip()
        origins: list[str] = []
        if value.startswith("["):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    origins = [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                origins = []
        elif value:
            origins = [item.strip() for item in value.split(",") if item.strip()]

        # Keep local development resilient when an older .env still lists a
        # previous frontend port. Vite currently runs on 3010.
        if self.app_env == "development":
            local_origins = [
                "http://localhost:3010",
                "http://127.0.0.1:3010",
            ]
            for origin in local_origins:
                if origin not in origins:
                    origins.append(origin)

        return origins

    @property
    def sqlalchemy_database_url(self) -> str:
        return normalize_database_url(self.database_url)


def is_production_runtime(settings: "Settings") -> bool:
    return settings.app_env == "production" or os.getenv("VERCEL_ENV") == "production"


def production_configuration_errors(settings: "Settings") -> list[str]:
    """Report production configuration problems without preventing app import."""
    if not is_production_runtime(settings):
        return []

    errors: list[str] = []
    if settings.app_env != "production":
        errors.append("APP_ENV must be set to production")
    database_url = settings.sqlalchemy_database_url.strip()
    if not database_url.startswith("postgresql+psycopg://"):
        errors.append("DATABASE_URL must be a PostgreSQL/Supabase connection string")

    email = settings.admin_email.strip().lower()
    if not email or email == "admin@onatowers.dev":
        errors.append("ADMIN_EMAIL must be set to the real production administrator email")

    password = settings.admin_password
    insecure_passwords = {"ona-admin-local", "Oniria@1234."}
    if len(password) < 12 or password in insecure_passwords:
        errors.append("ADMIN_PASSWORD must be a unique production password of at least 12 characters")

    secret = settings.admin_session_secret
    if len(secret) < 32 or secret == "ona-local-development-secret":
        errors.append("ADMIN_SESSION_SECRET must be a unique random value of at least 32 characters")

    if settings.auto_init_db:
        errors.append("AUTO_INIT_DB must remain false in production; use Alembic migrations instead")

    return errors


def validate_production_settings(settings: "Settings") -> None:
    """Keep database seeding strict while health checks remain diagnostic."""
    errors = production_configuration_errors(settings)
    if errors:
        joined = "; ".join(errors)
        raise RuntimeError(f"Invalid production configuration: {joined}.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
