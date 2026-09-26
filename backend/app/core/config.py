from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent

DEFAULT_DATABASE_URL = "sqlite+pysqlite:///./database/ona_towers.db"

DEFAULT_ADMIN_EMAIL = "admin@onatowers.dev"
DEFAULT_ADMIN_PASSWORD = "ona-admin-local"
DEFAULT_ADMIN_SESSION_SECRET = "ona-local-development-secret"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(PROJECT_ROOT / ".env"),
            str(BACKEND_DIR / ".env"),
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ONA Towers API"
    app_env: str = "development"
    app_debug: bool = True

    api_prefix: str = "/api"
    log_level: str = "INFO"

    auto_init_db: bool = False

    database_url: str = DEFAULT_DATABASE_URL
    migration_database_url: str = ""

    cors_origins: str = (
        "http://localhost:3010,"
        "http://127.0.0.1:3010"
    )
    cors_origin_regex: str = ""

    enquiry_rate_limit_count: int = 5
    enquiry_rate_limit_window_seconds: int = 3600
    duplicate_enquiry_window_seconds: int = 120
    max_message_length: int = 2000

    smtp_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "ONA Towers"
    smtp_use_tls: bool = True
    sales_notification_email: str = ""

    admin_email: str = DEFAULT_ADMIN_EMAIL
    admin_password: str = DEFAULT_ADMIN_PASSWORD

    admin_name: str = "ONA Administrator"
    admin_role: str = "Administrator"
    admin_department: str = "Administration"

    admin_session_secret: str = DEFAULT_ADMIN_SESSION_SECRET
    admin_session_hours: int = 12

    @field_validator(
        "app_env",
        mode="before",
    )
    @classmethod
    def normalize_app_env(
        cls,
        value: object,
    ) -> str:
        if value is None:
            return "development"

        return str(value).strip().lower()

    @field_validator(
        "log_level",
        mode="before",
    )
    @classmethod
    def normalize_log_level(
        cls,
        value: object,
    ) -> str:
        if value is None:
            return "INFO"

        return str(value).strip().upper()

    @field_validator(
        "api_prefix",
        mode="before",
    )
    @classmethod
    def normalize_api_prefix(
        cls,
        value: object,
    ) -> str:
        if value is None:
            return "/api"

        prefix = str(value).strip()

        if not prefix:
            return "/api"

        if not prefix.startswith("/"):
            prefix = f"/{prefix}"

        if len(prefix) > 1:
            prefix = prefix.rstrip("/")

        return prefix

    @field_validator(
        "database_url",
        "migration_database_url",
        mode="before",
    )
    @classmethod
    def normalize_database_url(
        cls,
        value: object,
    ) -> str:
        if value is None:
            return ""

        url = str(value).strip()

        if not url:
            return ""

        if url.startswith(
            "postgres://"
        ):
            return url.replace(
                "postgres://",
                "postgresql+psycopg://",
                1,
            )

        if url.startswith(
            "postgresql://"
        ):
            return url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1,
            )

        return url

    @property
    def cors_origins_list(
        self,
    ) -> list[str]:
        if not self.cors_origins:
            return []

        return [
            origin.strip()
            for origin
            in self.cors_origins.split(",")
            if origin.strip()
        ]


def is_production_runtime(
    settings: Settings,
) -> bool:
    if (
        settings.app_env
        == "production"
    ):
        return True

    vercel_env = (
        os.getenv(
            "VERCEL_ENV",
            "",
        )
        .strip()
        .lower()
    )

    return (
        vercel_env
        == "production"
    )


def _contains_placeholder(
    value: str,
) -> bool:
    lowered = value.lower()

    placeholders = (
        "your_project_ref",
        "your-project-ref",
        "your_password",
        "your-password",
        "[your-password]",
        "replace_me",
        "replace-me",
        "example_password",
    )

    return any(
        placeholder
        in lowered
        for placeholder
        in placeholders
    )


def _database_backend(
    database_url: str,
) -> str:
    lowered = (
        database_url
        .strip()
        .lower()
    )

    if not lowered:
        return "missing"

    if lowered.startswith(
        "sqlite"
    ):
        return "sqlite"

    if lowered.startswith(
        (
            "postgresql://",
            "postgresql+psycopg://",
            "postgres://",
        )
    ):
        return "postgresql"

    return "unknown"


def production_configuration_errors(
    settings: Settings,
) -> list[str]:
    if not is_production_runtime(
        settings
    ):
        return []

    errors: list[str] = []

    if (
        settings.app_env
        != "production"
    ):
        errors.append(
            "APP_ENV must be "
            "'production'."
        )

    if settings.app_debug:
        errors.append(
            "APP_DEBUG must be "
            "false in production."
        )

    if settings.auto_init_db:
        errors.append(
            "AUTO_INIT_DB must be "
            "false in production."
        )

    database_url = (
        settings.database_url
        .strip()
    )

    if not database_url:
        errors.append(
            "DATABASE_URL is missing."
        )

    elif database_url.lower().startswith(
        "sqlite"
    ):
        errors.append(
            "DATABASE_URL cannot use "
            "SQLite in production."
        )

    elif _contains_placeholder(
        database_url
    ):
        errors.append(
            "DATABASE_URL contains "
            "placeholder values."
        )

    elif _database_backend(
        database_url
    ) != "postgresql":
        errors.append(
            "DATABASE_URL must use "
            "PostgreSQL in production."
        )

    admin_email = (
        settings.admin_email
        .strip()
    )

    if not admin_email:
        errors.append(
            "ADMIN_EMAIL is missing."
        )

    elif (
        admin_email.lower()
        == DEFAULT_ADMIN_EMAIL.lower()
    ):
        errors.append(
            "ADMIN_EMAIL is still using "
            "the development default."
        )

    admin_password = (
        settings.admin_password
    )

    if not admin_password:
        errors.append(
            "ADMIN_PASSWORD is missing."
        )

    elif (
        admin_password
        == DEFAULT_ADMIN_PASSWORD
    ):
        errors.append(
            "ADMIN_PASSWORD is still "
            "using the development default."
        )

    elif len(
        admin_password
    ) < 12:
        errors.append(
            "ADMIN_PASSWORD must contain "
            "at least 12 characters."
        )

    session_secret = (
        settings.admin_session_secret
    )

    if not session_secret:
        errors.append(
            "ADMIN_SESSION_SECRET "
            "is missing."
        )

    elif (
        session_secret
        == DEFAULT_ADMIN_SESSION_SECRET
    ):
        errors.append(
            "ADMIN_SESSION_SECRET is "
            "still using the development "
            "default."
        )

    elif len(
        session_secret
    ) < 32:
        errors.append(
            "ADMIN_SESSION_SECRET must "
            "contain at least 32 characters."
        )

    if (
        settings.admin_session_hours
        < 1
        or
        settings.admin_session_hours
        > 168
    ):
        errors.append(
            "ADMIN_SESSION_HOURS must "
            "be between 1 and 168."
        )

    if settings.smtp_enabled:
        if not settings.smtp_host:
            errors.append(
                "SMTP_HOST is required "
                "when SMTP_ENABLED=true."
            )

        if not settings.smtp_from_email:
            errors.append(
                "SMTP_FROM_EMAIL is required "
                "when SMTP_ENABLED=true."
            )

    return errors


def runtime_configuration_snapshot(
    settings: Settings,
) -> dict[str, object]:
    database_url = (
        settings.database_url
        .strip()
    )

    database_backend = (
        _database_backend(
            database_url
        )
    )

    admin_email_configured = (
        bool(
            settings.admin_email
            .strip()
        )
        and
        settings.admin_email.lower()
        != DEFAULT_ADMIN_EMAIL.lower()
    )

    admin_password_configured = (
        bool(
            settings.admin_password
        )
        and
        settings.admin_password
        != DEFAULT_ADMIN_PASSWORD
    )

    admin_session_secret_configured = (
        bool(
            settings.admin_session_secret
        )
        and
        settings.admin_session_secret
        != DEFAULT_ADMIN_SESSION_SECRET
    )

    errors = (
        production_configuration_errors(
            settings
        )
    )

    return {
        "production_runtime":
            is_production_runtime(
                settings
            ),

        "app_env":
            settings.app_env,

        "app_debug":
            settings.app_debug,

        "auto_init_db":
            settings.auto_init_db,

        "api_prefix":
            settings.api_prefix,

        "database_configured":
            bool(
                database_url
            ),

        "database_backend":
            database_backend,

        "database_is_supabase":
            (
                "supabase"
                in database_url.lower()
                or
                "pooler.supabase.com"
                in database_url.lower()
            ),

        "admin_email_configured":
            admin_email_configured,

        "admin_password_configured":
            admin_password_configured,

        "admin_session_secret_configured":
            admin_session_secret_configured,

        "smtp_enabled":
            settings.smtp_enabled,

        "production_configuration_valid":
            len(errors) == 0,

        "production_configuration_errors":
            errors,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()