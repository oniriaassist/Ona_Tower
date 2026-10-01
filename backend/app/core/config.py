from functools import lru_cache
from pathlib import Path
from typing import Literal
from email.utils import parseaddr
from urllib.parse import urlsplit
import json
import os
import re

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


DEFAULT_CITYVIEW_URL = "https://www.onatowers.com/cityview"
MARKDOWN_LINK_RE = re.compile(r"^\[.*?\]\((https?://[^)]+)\)$", re.IGNORECASE)


def normalize_public_url(value: str | None, default: str = DEFAULT_CITYVIEW_URL) -> str:
    """Return a clean absolute public URL.

    This also repairs an accidentally pasted Markdown link such as
    ``[https://example.com](https://example.com)`` from an environment variable.
    """
    raw = (value or "").strip().strip('"').strip("'")
    markdown_match = MARKDOWN_LINK_RE.match(raw)
    if markdown_match:
        raw = markdown_match.group(1).strip()

    raw = raw.replace("\\)", ")").replace("\\]", "]")
    try:
        parsed = urlsplit(raw)
    except ValueError:
        return default
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return default
    return raw


def email_domain(value: str | None) -> str:
    """Extract a lowercase domain from a mailbox value."""
    address = parseaddr((value or "").strip())[1]
    if "@" not in address:
        return ""
    return address.rsplit("@", 1)[1].strip().lower().rstrip(".")


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
    resend_from_email: str = "sales@onatowers.com"
    resend_sending_domain: str = "onatowers.com"
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
    cityview_url: str = DEFAULT_CITYVIEW_URL

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

    @property
    def uses_resend_transport(self) -> bool:
        """Return whether email is delivered by Resend API or Resend SMTP."""
        if self.effective_email_provider == "resend":
            return True
        if self.effective_email_provider != "smtp":
            return False
        host = (self.smtp_host or "").strip().lower().rstrip(".")
        return host == "smtp.resend.com" or host.endswith(".smtp.resend.com")

    @property
    def effective_from_email(self) -> str:
        """Choose the sender mailbox for the active transport.

        Any Resend transport deliberately uses RESEND_FROM_EMAIL instead of
        SMTP_FROM_EMAIL. This prevents a legacy Proton mailbox from being used
        as the Resend ``from`` address and rejected with HTTP 403.
        """
        if self.uses_resend_transport:
            return (self.resend_from_email or "").strip()
        return (self.smtp_from_email or "").strip()

    @property
    def cityview_public_url(self) -> str:
        return normalize_public_url(self.cityview_url, DEFAULT_CITYVIEW_URL)

    @property
    def resend_sender_domain_matches(self) -> bool:
        if not self.uses_resend_transport:
            return True
        expected = (self.resend_sending_domain or "").strip().lower().rstrip(".")
        actual = email_domain(self.effective_from_email)
        return bool(expected and actual and actual == expected)


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
        if not settings.effective_from_email:
            warnings.append("A sender email is required for transactional email delivery")
        if provider == "none":
            warnings.append("No email provider is configured; set RESEND_API_KEY or SMTP_HOST")
        elif provider == "resend":
            if not (settings.resend_api_key or "").strip():
                warnings.append("EMAIL_PROVIDER=resend requires RESEND_API_KEY")
        elif provider == "smtp":
            if not settings.smtp_host:
                warnings.append("EMAIL_PROVIDER=smtp requires SMTP_HOST")
            if bool(settings.smtp_username) != bool(settings.smtp_password):
                warnings.append("SMTP_USERNAME and SMTP_PASSWORD should either both be set or both be empty")
        if settings.uses_resend_transport and not settings.resend_sender_domain_matches:
            warnings.append(
                f"RESEND_FROM_EMAIL must use the configured Resend sending domain {settings.resend_sending_domain}"
            )
        if not settings.sales_notification_email:
            warnings.append("SALES_NOTIFICATION_EMAIL is not set; customer auto-replies can send but staff email notifications will be skipped")
        if settings.cityview_public_url != (settings.cityview_url or "").strip():
            warnings.append("CITYVIEW_URL was not a plain absolute URL; a safe City View URL will be used")

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
