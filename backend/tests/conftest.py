import os
os.environ["APP_ENV"] = "test"
os.environ["APP_DEBUG"] = "false"
os.environ["ENQUIRY_RATE_LIMIT_COUNT"] = "100"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["AUTO_INIT_DB"] = "true"
# Keep test authentication independent of local credentials.
os.environ["ADMIN_EMAIL"] = "admin@onatowers.dev"
os.environ["ADMIN_PASSWORD"] = "ona-admin-local"
os.environ["ADMIN_NAME"] = "ONA Administrator"
os.environ["ADMIN_ROLE"] = "Administrator"
os.environ["ADMIN_DEPARTMENT"] = "Administration"
os.environ["ADMIN_SESSION_SECRET"] = "ona-local-development-secret"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.dependencies import get_repository
from app.repositories.memory import InMemoryRepository


@pytest.fixture
def repository():
    return InMemoryRepository()


@pytest.fixture
def client(repository):
    app.dependency_overrides[get_repository] = lambda: repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
