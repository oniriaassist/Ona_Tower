import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def test_deployment_keeps_runtime_packages(tmp_path):
    files = subprocess.check_output(
        ["git", "ls-files", "backend"], cwd=ROOT, text=True,
    ).splitlines()
    ignored = subprocess.run(
        ["git", "-c", "core.excludesFile=.vercelignore", "check-ignore", "--no-index", "--stdin"],
        input="\n".join(files) + "\n", cwd=ROOT, capture_output=True, text=True,
    )
    assert ignored.returncode in (0, 1), ignored.stderr
    excluded = set(ignored.stdout.splitlines())
    assert not any(path.startswith("backend/app/") for path in excluded)
    for path in files:
        if path not in excluded:
            target = tmp_path / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, target)
    env = dict(os.environ, AUTO_INIT_DB="false")
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-c", (
            "import importlib.util; "
            "spec = importlib.util.spec_from_file_location('deployment_main', 'backend/main.py'); "
            "module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); "
            "from fastapi.testclient import TestClient; "
            "client = TestClient(module.app); "
            "assert client.get('/health').status_code == 200; "
            "assert '/api/enquiries' in module.app.openapi()['paths']"
        )], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_migrated_database_enquiry_round_trip(tmp_path):
    env = dict(
        os.environ, AUTO_INIT_DB="false", SMTP_ENABLED="false",
        DATABASE_URL="sqlite+pysqlite:///" + (tmp_path / "integration.db").as_posix(),
        PYTHONPATH=str(ROOT / "backend"),
    )
    env["MIGRATION_DATABASE_URL"] = env["DATABASE_URL"]
    for command in [
        ["-m", "alembic", "-c", "database/alembic.ini", "upgrade", "head"],
        ["scripts/db_seed.py"],
        ["scripts/db_check.py"],
        ["-c", """
from fastapi.testclient import TestClient
from main import app
with TestClient(app) as client:
    assert client.get('/health/database').status_code == 200
    assert client.get('/api/residences').status_code == 200
    result = client.post('/api/enquiries', json={
        'name': 'Deployment Integration', 'phone': '+255777555444',
        'email': 'deployment@example.com', 'enquiry_type': 'general',
        'message': 'Please send residence information.', 'consent': True,
        'source': 'website', 'company_website': '',
    })
    assert result.status_code == 201, result.text
    reference = result.json()['reference_number']
    login = client.post('/api/admin/login', json={
        'email': 'admin@onatowers.dev', 'password': 'ona-admin-local',
    })
    assert login.status_code == 200, login.text
    listing = client.get('/api/admin/enquiries', headers={
        'Authorization': 'Bearer ' + login.json()['token'],
    })
    assert listing.status_code == 200, listing.text
    assert any(row['reference_number'] == reference for row in listing.json()['items'])
"""],
    ]:
        result = subprocess.run(
            [sys.executable, *command], cwd=ROOT, env=env,
            capture_output=True, text=True, timeout=40,
        )
        assert result.returncode == 0, result.stdout + result.stderr
