import io
import time


def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_readiness_check(client):
    resp = client.get("/api/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["database"] == "ok"
    assert "status" in body


def test_authentication_register_and_login(client):
    email = "testauth@example.com"
    pwd = "ValidPassword123!"

    resp = client.post("/api/auth/register", json={"email": email, "password": pwd})
    assert resp.status_code == 201
    assert resp.json()["email"] == email

    resp = client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

    resp = client.post("/api/auth/login", json={"email": email, "password": "wrongpassword"})
    assert resp.status_code == 401


def test_api_upload_requires_auth(client):
    resp = client.post("/api/reports/upload", files={"file": ("test.txt", b"hello", "text/plain")})
    assert resp.status_code in (401, 403)


def test_api_upload_and_status(client, auth_headers):
    file_content = b"Hemoglobin 10.2 g/dL 12.0-16.0\nWBC 7200 /uL 4000-11000\nGlucose 128 mg/dL 70-100"
    resp = client.post(
        "/api/reports/upload",
        files={"file": ("report.txt", io.BytesIO(file_content), "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "report_id" in body
    assert "job_id" in body
    assert body["status"] == "queued"

    report_id = body["report_id"]

    # Give pipeline a moment to finish via background thread
    time.sleep(0.5)

    # Check status endpoint
    status_resp = client.get(f"/api/reports/{report_id}/status", headers=auth_headers)
    assert status_resp.status_code == 200
    assert "stage" in status_resp.json()
    assert "progress" in status_resp.json()


def test_user_report_isolation(client):
    # User 1 registers and uploads
    client.post("/api/auth/register", json={"email": "u1@isolation.com", "password": "password123"})
    token1 = client.post("/api/auth/login", json={"email": "u1@isolation.com", "password": "password123"}).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    resp = client.post(
        "/api/reports/upload",
        files={"file": ("isolated.txt", io.BytesIO(b"Glucose 90 mg/dL 70-100"), "text/plain")},
        headers=headers1,
    )
    report_id = resp.json()["report_id"]

    # User 2 tries to access user 1's report -> Must return 404 (Requirement #22)
    client.post("/api/auth/register", json={"email": "u2@isolation.com", "password": "password123"})
    token2 = client.post("/api/auth/login", json={"email": "u2@isolation.com", "password": "password123"}).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp = client.get(f"/api/reports/{report_id}", headers=headers2)
    assert resp.status_code == 404

    resp = client.get(f"/api/reports/{report_id}/findings", headers=headers2)
    assert resp.status_code == 404

    resp = client.delete(f"/api/reports/{report_id}", headers=headers2)
    assert resp.status_code == 404
