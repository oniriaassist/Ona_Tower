import pytest

from app.core.config import Settings, normalize_public_url, validate_production_settings


def test_production_settings_reject_development_defaults():
    settings = Settings(_env_file=None, app_env="production")

    with pytest.raises(RuntimeError, match="Invalid production configuration"):
        validate_production_settings(settings)


def test_production_settings_accept_supabase_runtime_values():
    settings = Settings(
        _env_file=None,
        app_env="production",
        app_debug=False,
        auto_init_db=False,
        database_url=(
            "postgresql://postgres.project-ref:password@"
            "aws-0-region.pooler.supabase.com:6543/postgres?sslmode=require"
        ),
        admin_email="admin@example.com",
        admin_password="unique-production-password",
        admin_session_secret="x" * 48,
    )

    validate_production_settings(settings)
    assert settings.sqlalchemy_database_url.startswith("postgresql+psycopg://")


def test_production_postgres_uses_null_pool_and_disables_prepared_statements():
    from sqlalchemy.pool import NullPool
    from app.database.session import build_engine_options

    settings = Settings(
        _env_file=None,
        app_env="production",
        database_url=(
            "postgresql://postgres.project-ref:password@"
            "aws-0-region.pooler.supabase.com:6543/postgres?sslmode=require"
        ),
        admin_email="admin@example.com",
        admin_password="unique-production-password",
        admin_session_secret="x" * 48,
    )
    options = build_engine_options(settings)

    assert options["poolclass"] is NullPool
    assert options["connect_args"]["prepare_threshold"] is None


def test_supabase_sslmode_is_added_automatically():
    settings = Settings(
        _env_file=None,
        app_env="production",
        app_debug=False,
        auto_init_db=False,
        database_url=(
            "postgresql://postgres.project-ref:password@"
            "aws-1-region.pooler.supabase.com:6543/postgres"
        ),
        admin_email="admin@example.com",
        admin_password="shortpass",
        admin_session_secret="x" * 48,
    )

    assert settings.sqlalchemy_database_url.endswith("?sslmode=require")
    validate_production_settings(settings)


def test_weak_bootstrap_password_is_not_a_global_service_error():
    from app.core.config import production_configuration_errors, production_configuration_warnings

    settings = Settings(
        _env_file=None,
        app_env="production",
        app_debug=False,
        auto_init_db=False,
        database_url=(
            "postgresql://postgres.project-ref:password@"
            "aws-1-region.pooler.supabase.com:6543/postgres"
        ),
        admin_email="admin@example.com",
        admin_password="shortpass",
        admin_session_secret="x" * 48,
    )

    assert production_configuration_errors(settings) == []
    assert any("ADMIN_PASSWORD" in warning for warning in production_configuration_warnings(settings))


def test_markdown_cityview_url_is_normalized():
    value = "[https://www.onatowers.com/cityview](https://www.onatowers.com/cityview)"
    assert normalize_public_url(value) == "https://www.onatowers.com/cityview"


def test_resend_uses_its_verified_sender_not_legacy_smtp_sender():
    settings = Settings(
        _env_file=None,
        email_provider="resend",
        resend_api_key="re_test",
        smtp_from_email="onatowers@proton.me",
    )
    assert settings.effective_from_email == "sales@onatowers.com"
    assert settings.resend_sender_domain_matches is True
