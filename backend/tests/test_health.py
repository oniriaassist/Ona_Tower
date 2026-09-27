def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_skips_configuration_validation(client, monkeypatch):
    from app import main

    def fail_validation(_):
        raise RuntimeError("private configuration")

    monkeypatch.setattr(main, "production_configuration_errors", fail_validation)
    assert client.get("/health").status_code == 200


def test_configuration_exception_is_redacted(client, monkeypatch):
    from app.api.routes import health

    def fail_settings():
        raise ValueError("private configuration")

    monkeypatch.setattr(health, "get_settings", fail_settings)
    response = client.get("/health/config")
    assert response.status_code == 503
    assert response.json()["detail"]["error_type"] == "ValueError"
    assert "private configuration" not in response.text


def test_database_health(client):
    response = client.get("/health/database")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_configuration_health_reports_problems(client, monkeypatch):
    from app.api.routes import health
    from app.core.config import Settings

    settings = Settings(_env_file=None, app_env="production", database_url="invalid")
    monkeypatch.setattr(health, "get_settings", lambda: settings)
    response = client.get("/health/config")
    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "misconfigured"
    assert "DATABASE_URL" in response.json()["detail"]["errors"][0]
    assert client.get("/health").status_code == 200


def test_database_failure_preserves_liveness(client, monkeypatch):
    from app.database import session

    def fail_engine():
        raise ValueError("private database connection details")

    monkeypatch.setattr(session, "get_engine", fail_engine)
    response = client.get("/health/database")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection unavailable"
    assert "private" not in response.text
    assert client.get("/health").status_code == 200


def test_production_import_does_not_create_engine():
    import os
    from pathlib import Path
    import subprocess
    import sys

    env = dict(os.environ, APP_ENV="production", AUTO_INIT_DB="false", DATABASE_URL="invalid")
    result = subprocess.run(
        [sys.executable, "-c", (
            "from unittest.mock import patch; "
            "guard = patch('sqlalchemy.create_engine', side_effect=AssertionError('eager engine')); "
            "guard.start(); "
            "from app.main import app; "
            "from fastapi.testclient import TestClient; "
            "client = TestClient(app); "
            "assert client.get('/health').status_code == 200; "
            "assert client.get('/health/config').status_code == 503; "
            "response = client.get('/api/residences'); "
            "assert response.status_code == 503; "
            "assert response.json()['code'] == 'service_misconfigured'; "
            "assert client.get('/health/database').status_code == 503"
        )],
        cwd=Path(__file__).resolve().parents[1], env=env,
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_database_repository_and_readiness(client):
    from app.database.check import main
    from app.repositories.dependencies import get_repository

    assert main() == 0
    client.app.dependency_overrides.pop(get_repository)
    assert client.get("/api/residences").status_code == 200


def test_vercel_production_guard(client, monkeypatch):
    monkeypatch.setenv("VERCEL_ENV", "production")
    assert client.get("/health").status_code == 200
    response = client.get("/health/config")
    assert response.status_code == 503
    assert "APP_ENV must be set to production" in response.json()["detail"]["errors"]
    response = client.post("/api/admin/login", json={})
    assert response.status_code == 503
    assert response.json()["code"] == "service_misconfigured"


def test_configuration_health_keeps_hardening_warnings_non_fatal(client, monkeypatch):
    from app.api.routes import health
    from app.core.config import Settings

    settings = Settings(
        _env_file=None,
        app_env="production",
        app_debug=False,
        auto_init_db=False,
        database_url=(
            "postgresql://postgres.project-ref:password@"
            "aws-1-region.pooler.supabase.com:5432/postgres"
        ),
        admin_email="admin@example.com",
        admin_password="shortpass",
        admin_session_secret="x" * 48,
    )
    monkeypatch.setattr(health, "get_settings", lambda: settings)

    response = client.get("/health/config")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database_ssl_required"] is True
    assert any("ADMIN_PASSWORD" in warning for warning in response.json()["warnings"])


def test_production_hardening_warnings_do_not_block_customer_api():
    import os
    from pathlib import Path
    import subprocess
    import sys

    env = dict(
        os.environ,
        APP_ENV="production",
        VERCEL_ENV="production",
        APP_DEBUG="false",
        AUTO_INIT_DB="false",
        DATABASE_URL=(
            "postgresql://postgres.project-ref:password@"
            "aws-1-region.pooler.supabase.com:5432/postgres"
        ),
        ADMIN_EMAIL="admin@example.com",
        ADMIN_PASSWORD="shortpass",
        ADMIN_SESSION_SECRET="x" * 48,
    )
    result = subprocess.run(
        [sys.executable, "-c", (
            "from app.main import app; "
            "from app.repositories.dependencies import get_repository; "
            "from app.repositories.memory import InMemoryRepository; "
            "from fastapi.testclient import TestClient; "
            "app.dependency_overrides[get_repository] = lambda: InMemoryRepository(); "
            "client = TestClient(app); "
            "cfg = client.get('/api/health/config'); "
            "assert cfg.status_code == 200, cfg.text; "
            "assert cfg.json()['database_ssl_required'] is True; "
            "assert cfg.json()['warnings']; "
            "response = client.get('/api/residences'); "
            "assert response.status_code == 200, response.text"
        )],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
