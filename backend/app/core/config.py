from functools import lru_cache
from pathlib import Path
from typing import Literal
import json
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


def normalize_database_url(url: str | None) -> str:
    """Normalize database URLs for local, Supabase, and Vercel runtimes.

    Supabase recommends SSL for Postgres connections. Production should not
    become unavailable just because ``sslmode=require`` was omitted from the
    dashboard value, so we add it automatically for Supabase URLs.
    """
    value = (url or "").strip()
    if not value:
        return ""

    if value.startswith("sqlite+pysqlite:///./"):
        relative_path = value[len("sqlite+pysqlite:///./"):]
        return f"sqlite+pysqlite:///{(PROJECT_ROOT / relative_path).resolve().as_posix()}"

    if value.startswith("sqlite:///./"):
        relative_path = value[len("sqlite:///./"):]
        return f"sqlite+pysqlite:///{(PROJECT_ROOT / relative_path).resolve().as_posix()}"

    if value.startswith("postgres://"):
        value = "postgresql+psycopg://" + value[len("postgres://"):]
    elif value.startswith("postgresql://"):
        value = "postgresql+psycopg://" + value[len("postgresql://"):]
    elif value.startswith("postgresql+psycopg2://"):
        value = "postgresql+psycopg://" + value[len("postgresql+psycopg2://"):]

    lowered = value.lower()
    if value.startswith("postgresql+psycopg://") and "supabase" in lowered and "sslmode=" not in lowered:
        separator = "&" if "?" in value else "?"
        value = f"{value}{separator}sslmode=require"

    return value


class Settings(BaseSettings):
    app_name: str = "ONA Towers API"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_debug: bool = True
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8400
    cors_origins: str = "http://localhost:3010,http://127.0.0.1:3010"
    cors_origin_regex: str | None = None
    log_level: str = "INFO"

    database_url: str = "sqlite+pysqlite:///./database/ona_towers.db"
    auto_init_db: bool = False

    enquiry_rate_limit_count: int = 5
    enquiry_rate_limit_window_seconds: int = 3600
    duplicate_enquiry_window_seconds: int = 120
    max_message_length: int = 2000

    email_enabled: bool | None = None
    email_provider: Literal["auto", "resend", "smtp"] = "auto"
    resend_api_key: str | None = None
    resend_api_url: str = "https://api.resend.com/emails"
    email_timeout_seconds: int = 12

    # Backward-compatible SMTP settings. SMTP_ENABLED is still honored when
    # EMAIL_ENABLED is not explicitly set.
    smtp_enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = "ONA Towers"
    smtp_use_tls: bool = True
    sales_notification_email: str | None = None
    cityview_url: str = "https://www.onatowers.com/cityview"

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

        if self.app_env == "development":
            for origin in ("http://localhost:3010", "http://127.0.0.1:3010"):
                if origin not in origins:
                    origins.append(origin)
        return origins

    @property
    def sqlalchemy_database_url(self) -> str:
        return normalize_database_url(self.database_url)

    @property
    def email_delivery_enabled(self) -> bool:
        """Return whether transactional email delivery is enabled.

        EMAIL_ENABLED is the preferred switch. For backward compatibility, an
        existing SMTP_ENABLED=true deployment still works. Supplying a Resend
        API key also enables delivery when EMAIL_ENABLED was not explicitly set.
        """
        if self.email_enabled is not None:
            return self.email_enabled
        return self.smtp_enabled or bool((self.resend_api_key or "").strip())

    @property
    def effective_email_provider(self) -> str:
        """Choose the configured email transport without exposing secrets."""
        if self.email_provider == "resend":
            return "resend"
        if self.email_provider == "smtp":
            return "smtp"
        if (self.resend_api_key or "").strip():
            return "resend"
        if (self.smtp_host or "").strip():
            return "smtp"
        return "none"


def is_production_runtime(settings: "Settings") -> bool:
    return settings.app_env == "production" or os.getenv("VERCEL_ENV") == "production"


def production_configuration_errors(settings: "Settings") -> list[str]:
    """Return only faults that make the API operationally unable to run.

    Security-quality recommendations are deliberately warnings, not global
    service blockers. A weak bootstrap admin password must never take customer
    residence/enquiry endpoints offline.
    """
    if not is_production_runtime(settings):
        return []

    errors: list[str] = []
    if settings.app_env != "production":
        errors.append("APP_ENV must be set to production")

    database_url = settings.sqlalchemy_database_url.strip()
    if not database_url.startswith("postgresql+psycopg://"):
        errors.append("DATABASE_URL must be a PostgreSQL/Supabase connection string")
    else:
        lowered_database_url = database_url.lower()
        placeholders = (
            "your_project_ref",
            "project_ref",
            "pooler_host",
            "your_password",
            "password_here",
        )
        if any(value in lowered_database_url for value in placeholders):
            errors.append("DATABASE_URL still contains a placeholder value")

    return errors


def production_configuration_warnings(settings: "Settings") -> list[str]:
    """Return non-fatal production hardening recommendations."""
    if not is_production_runtime(settings):
        return []

    warnings: list[str] = []
    raw_database_url = settings.database_url.strip().lower()
    normalized_database_url = settings.sqlalchemy_database_url.lower()

    if "supabase" in raw_database_url and "sslmode=" not in raw_database_url:
        warnings.append("DATABASE_URL omitted sslmode; sslmode=require is applied automatically")

    if "supabase" in normalized_database_url and ":6543/" not in normalized_database_url:
        warnings.append("Supabase Transaction pooler port 6543 is recommended for Vercel serverless runtime")

    email = settings.admin_email.strip().lower()
    if not email or email == "admin@onatowers.dev":
        warnings.append("ADMIN_EMAIL should be changed from the development default")

    password = settings.admin_password
    insecure_passwords = {"ona-admin-local", "Oniria@1234."}
    if len(password) < 12 or password in insecure_passwords:
        warnings.append("ADMIN_PASSWORD should be a unique production password of at least 12 characters")

    secret = settings.admin_session_secret
    if len(secret) < 32 or secret == "ona-local-development-secret":
        warnings.append("ADMIN_SESSION_SECRET should be a unique random value of at least 32 characters")

    if settings.auto_init_db:
        warnings.append("AUTO_INIT_DB should remain false in production; use Alembic migrations instead")

    if not settings.email_delivery_enabled:
        warnings.append("Transactional email is disabled; customer auto-replies and staff email notifications will not be sent")
    else:
        provider = settings.effective_email_provider
        if not settings.smtp_from_email:
            warnings.append("SMTP_FROM_EMAIL is required for transactional email delivery")
        if provider == "none":
            warnings.append("No email provider is configured; set RESEND_API_KEY or SMTP_HOST")
        elif provider == "resend" and not (settings.resend_api_key or "").strip():
            warnings.append("EMAIL_PROVIDER=resend requires RESEND_API_KEY")
        elif provider == "smtp":
            if not settings.smtp_host:
                warnings.append("EMAIL_PROVIDER=smtp requires SMTP_HOST")
            if bool(settings.smtp_username) != bool(settings.smtp_password):
                warnings.append("SMTP_USERNAME and SMTP_PASSWORD should either both be set or both be empty")
        if not settings.sales_notification_email:
            warnings.append("SALES_NOTIFICATION_EMAIL is not set; customer auto-replies can send but staff email notifications will be skipped")
        if not settings.cityview_url.strip().lower().startswith(("https://", "http://")):
            warnings.append("CITYVIEW_URL should be an absolute http(s) URL")

    return warnings


def validate_production_settings(settings: "Settings") -> None:
    """Raise only for configuration that prevents correct database operation."""
    errors = production_configuration_errors(settings)
    if errors:
        joined = "; ".join(errors)
        raise RuntimeError(f"Invalid production configuration: {joined}.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
