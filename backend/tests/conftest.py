import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use an isolated temp SQLite DB + upload dir for tests, set BEFORE importing app.
_tmp_dir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp_dir, 'test.db')}"
os.environ["UPLOAD_DIR"] = os.path.join(_tmp_dir, "uploads")
os.environ["SECRET_KEY"] = "test-secret"

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    email = "testuser@example.com"
    password = "SuperSecret123"
    client.post("/api/auth/register", json={"email": email, "password": password})
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
