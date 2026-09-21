import os
from pathlib import Path
import subprocess
import sys
import ast


def test_entrypoint_declares_app_at_module_scope():
    source = Path(__file__).resolve().parents[1] / "main.py"
    module = ast.parse(source.read_text(encoding="utf-8"))
    assert any(
        isinstance(statement, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "app" for target in statement.targets)
        for statement in module.body
    )


def test_entrypoint_exports_normal_application():
    from main import app
    from app.main import app as normal_app

    assert app is normal_app


def test_entrypoint_reports_invalid_settings_without_exposing_values():
    env = dict(os.environ, APP_DEBUG="private-invalid-value", AUTO_INIT_DB="false")
    result = subprocess.run(
        [sys.executable, "-c", (
            "from main import app; "
            "from fastapi.testclient import TestClient; "
            "client = TestClient(app); "
            "response = client.get('/health'); "
            "assert response.status_code == 503; "
            "assert response.json()['stage'] == 'bootstrap'; "
            "assert response.json()['error_type'] == 'ValidationError'; "
            "assert 'private-invalid-value' not in response.text; "
            "assert client.get('/docs').status_code == 404; "
            "assert client.get('/openapi.json').status_code == 404"
            "; response = client.post('/api/enquiries', json={}); "
            "assert response.status_code == 503; "
            "assert response.json()['code'] == 'service_bootstrap_failed'"
        )],
        cwd=Path(__file__).resolve().parents[1], env=env,
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
