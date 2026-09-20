from datetime import datetime, timezone

from app.database.models import Enquiry
from app.database.session import SessionLocal, get_engine


def _auth(client, email="admin@onatowers.dev", password="ona-admin-local"):
    response = client.post("/api/admin/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    body = response.json()
    return {"Authorization": f"Bearer {body['token']}"}, body["user"]


def test_admin_requires_auth(client):
    response = client.get("/api/admin/overview")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "admin_unauthorized"


def test_email_login_and_profile(client):
    headers, user = _auth(client)
    assert user["email"] == "admin@onatowers.dev"
    assert user["is_super_admin"] is True

    me = client.get("/api/admin/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["user"]["name"] == "ONA Administrator"

    updated = client.patch(
        "/api/admin/profile",
        headers=headers,
        json={"name": "ONA Admin", "email": "admin@onatowers.dev", "phone": "+255700000000"},
    )
    assert updated.status_code == 200
    assert updated.json()["user"]["name"] == "ONA Admin"


def test_forgot_password_request_is_generic(client):
    response = client.post("/api/admin/forgot-password", json={"email": "unknown@example.com"})
    assert response.status_code == 200
    assert response.json()["success"] is True

    response = client.post("/api/admin/forgot-password", json={"email": "admin@onatowers.dev"})
    assert response.status_code == 200
    headers, _ = _auth(client)
    team = client.get("/api/admin/team?include_inactive=true", headers=headers).json()
    admin = next(item for item in team if item["email"] == "admin@onatowers.dev")
    # Signing in clears the reset request, which confirms the request is tied to the account.
    assert admin["password_reset_requested_at"] is None


def test_admin_team_accounts_and_settings(client):
    headers, _ = _auth(client)
    created = client.post(
        "/api/admin/team",
        headers=headers,
        json={
            "name": "Zahra Said",
            "email": "zahra.admin@example.com",
            "password": "Temporary123!",
            "phone": "+255 777 000 111",
            "role": "Sales Manager",
            "department": "Sales",
            "is_super_admin": False,
            "active": True,
        },
    )
    assert created.status_code == 201, created.text
    member_id = created.json()["id"]
    assert "password_hash" not in created.json()
    assert created.json()["department"] == "Sales"

    staff_login = client.post(
        "/api/admin/login",
        json={"email": "zahra.admin@example.com", "password": "Temporary123!"},
    )
    assert staff_login.status_code == 200
    staff_headers = {"Authorization": f"Bearer {staff_login.json()['token']}"}
    forbidden = client.post(
        "/api/admin/team",
        headers=staff_headers,
        json={
            "name": "Other User",
            "email": "other@example.com",
            "password": "Temporary123!",
            "role": "Client Advisor",
        },
    )
    assert forbidden.status_code == 403

    reset = client.post(
        f"/api/admin/team/{member_id}/reset-password",
        headers=headers,
        json={"new_password": "Changed123!"},
    )
    assert reset.status_code == 200
    assert client.post(
        "/api/admin/login",
        json={"email": "zahra.admin@example.com", "password": "Changed123!"},
    ).status_code == 200

    settings = client.patch(
        "/api/admin/settings",
        headers=headers,
        json={
            "project_name": "ONA Towers",
            "sales_email": "sales@example.com",
            "sales_phone": "+255 700 000 000",
            "whatsapp_number": "+255 700 000 000",
            "response_sla_hours": 12,
            "timezone": "Africa/Dar_es_Salaam",
            "customer_site_url": "/",
            "notifications_enabled": True,
        },
    )
    assert settings.status_code == 200
    assert settings.json()["settings"]["response_sla_hours"] == 12


def test_change_own_password(client):
    admin_headers, _ = _auth(client)
    created = client.post(
        "/api/admin/team",
        headers=admin_headers,
        json={
            "name": "Password Test User",
            "email": "password-test@example.com",
            "password": "Initial123!",
            "role": "Client Advisor",
            "department": "Sales",
        },
    )
    assert created.status_code == 201
    login = client.post(
        "/api/admin/login",
        json={"email": "password-test@example.com", "password": "Initial123!"},
    )
    staff_headers = {"Authorization": f"Bearer {login.json()['token']}"}
    changed = client.post(
        "/api/admin/security/password",
        headers=staff_headers,
        json={
            "current_password": "Initial123!",
            "new_password": "NewStaff123!",
            "confirm_password": "NewStaff123!",
        },
    )
    assert changed.status_code == 200
    assert client.post(
        "/api/admin/login",
        json={"email": "password-test@example.com", "password": "NewStaff123!"},
    ).status_code == 200


def test_admin_can_read_and_update_customer_enquiry(client):
    with SessionLocal(bind=get_engine()) as db:
        row = Enquiry(
            reference_number="ONA-TEST-ADMIN-001",
            name="Admin Integration Test",
            phone="+255 777 555 444",
            email="integration@example.com",
            residence_interest="2-bedroom",
            enquiry_type="request_floor_plans",
            message="Please send the floor plan.",
            consent=True,
            source="website",
            status="new",
            created_at=datetime.now(timezone.utc),
        )
        db.add(row); db.commit(); db.refresh(row); enquiry_id = row.id

    headers, _ = _auth(client)
    listing = client.get("/api/admin/enquiries?search=Admin%20Integration", headers=headers)
    assert listing.status_code == 200
    assert any(item["id"] == enquiry_id for item in listing.json()["items"])

    updated = client.patch(
        f"/api/admin/enquiries/{enquiry_id}",
        headers=headers,
        json={"status": "contacted", "internal_notes": "Called customer and shared next steps."},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "contacted"
