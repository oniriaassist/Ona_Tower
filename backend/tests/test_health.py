def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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
            "assert client.get('/health/config').status_code == 503"
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
