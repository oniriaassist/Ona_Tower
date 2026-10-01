from datetime import datetime, timezone

from app.core.config import Settings
from app.schemas.enquiry import EnquiryRecord, EnquiryType
from app.services.notification import NotificationService


def _record() -> EnquiryRecord:
    return EnquiryRecord(
        id="enq-1",
        reference_number="ONA-20261001-ABC123",
        name="Test Customer",
        phone="+255777123456",
        email="customer@example.com",
        residence_interest="03 Bedroom Residence",
        enquiry_type=EnquiryType.enquire_about_residence,
        message="Please send availability.",
        consent=True,
        source="website",
        status="new",
        created_at=datetime.now(timezone.utc),
    )


def test_resend_configuration_is_ready_with_api_key():
    settings = Settings(
        _env_file=None,
        email_enabled=True,
        email_provider="resend",
        resend_api_key="re_test",
        # A legacy SMTP/Proton sender must not leak into the Resend From header.
        smtp_from_email="onatowers@proton.me",
        sales_notification_email="onatowers@proton.me",
        cityview_url="https://www.onatowers.com/cityview",
    )
    status = NotificationService(settings).configuration_status()
    assert status["ready"] is True
    assert status["provider"] == "resend"
    assert status["from_domain"] == "onatowers.com"
    assert status["resend_domain_match"] is True


def test_customer_and_staff_notifications_are_independent(monkeypatch):
    settings = Settings(
        _env_file=None,
        email_enabled=True,
        email_provider="resend",
        resend_api_key="re_test",
        smtp_from_email="onatowers@proton.me",
        sales_notification_email="onatowers@proton.me",
        cityview_url="[https://www.onatowers.com/cityview](https://www.onatowers.com/cityview)",
    )
    service = NotificationService(settings)
    delivered = []

    def fake_send(message, *, idempotency_key):
        if idempotency_key.startswith("ona-staff/"):
            raise RuntimeError("staff delivery unavailable")
        delivered.append((str(message["To"]), message.as_string(), idempotency_key))
        return "email-id"

    monkeypatch.setattr(service, "_send_message", fake_send)
    result = service.send_enquiry_notifications(_record())

    assert result.staff_sent is False
    assert result.customer_sent is True
    assert delivered[0][0] == "customer@example.com"
    assert "ONA Towers <sales@onatowers.com>" in delivered[0][1]
    assert "https://www.onatowers.com/cityview" in delivered[0][1]
    assert "[https://www.onatowers.com/cityview]" not in delivered[0][1]
    assert delivered[0][2] == "ona-customer/ONA-20261001-ABC123"


def test_email_disabled_reports_not_ready():
    settings = Settings(
        _env_file=None,
        email_enabled=False,
        smtp_from_email="sales@onatowers.com",
        cityview_url="https://www.onatowers.com/cityview",
    )
    status = NotificationService(settings).configuration_status()
    assert status["enabled"] is False
    assert status["ready"] is False
    assert any("disabled" in issue.lower() for issue in status["issues"])


def test_resend_wrong_sender_domain_is_not_ready():
    settings = Settings(
        _env_file=None,
        email_enabled=True,
        email_provider="resend",
        resend_api_key="re_test",
        resend_from_email="onatowers@proton.me",
        resend_sending_domain="onatowers.com",
    )
    status = NotificationService(settings).configuration_status()
    assert status["ready"] is False
    assert status["resend_domain_match"] is False
    assert any("sender domain mismatch" in issue.lower() for issue in status["issues"])


def test_cityview_markdown_link_is_normalized_in_customer_email(monkeypatch):
    settings = Settings(
        _env_file=None,
        email_enabled=True,
        email_provider="resend",
        resend_api_key="re_test",
        cityview_url="[https://www.onatowers.com/cityview](https://www.onatowers.com/cityview)",
    )
    service = NotificationService(settings)
    captured = {}

    def fake_send(message, *, idempotency_key):
        captured["message"] = message
        return "email-id"

    monkeypatch.setattr(service, "_send_message", fake_send)
    service._send_customer_acknowledgement(_record())
    raw = captured["message"].as_string()
    assert settings.cityview_public_url == "https://www.onatowers.com/cityview"
    assert "https://www.onatowers.com/cityview" in raw
    assert "[https://www.onatowers.com/cityview]" not in raw
    assert str(captured["message"]["From"]) == "ONA Towers <sales@onatowers.com>"


def test_resend_payload_uses_verified_ona_sender_and_plain_cityview_url(monkeypatch):
    settings = Settings(
        _env_file=None,
        email_enabled=True,
        email_provider="resend",
        resend_api_key="re_test",
        smtp_from_email="onatowers@proton.me",
        sales_notification_email="onatowers@proton.me",
        cityview_url="[https://www.onatowers.com/cityview](https://www.onatowers.com/cityview)",
    )
    service = NotificationService(settings)
    captured = {}

    class FakeResponse:
        is_error = False
        text = ""

        def json(self):
            return {"id": "resend-email-id"}

    class FakeClient:
        def __init__(self, *, timeout):
            captured["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, *, headers, json):
            captured["url"] = url
            captured["headers"] = headers
            captured["payload"] = json
            return FakeResponse()

    monkeypatch.setattr("app.services.notification.httpx.Client", FakeClient)
    service._send_customer_acknowledgement(_record())

    payload = captured["payload"]
    assert payload["from"] == "ONA Towers <sales@onatowers.com>"
    assert payload["reply_to"] == "onatowers@proton.me"
    assert "https://www.onatowers.com/cityview" in payload["text"]
    assert '[https://www.onatowers.com/cityview]' not in payload["text"]
    assert 'href="https://www.onatowers.com/cityview"' in payload["html"]
    assert captured["headers"]["Authorization"] == "Bearer re_test"


def test_resend_smtp_also_uses_verified_ona_sender():
    settings = Settings(
        _env_file=None,
        email_enabled=True,
        email_provider="smtp",
        smtp_host="smtp.resend.com",
        smtp_port=587,
        smtp_username="resend",
        smtp_password="re_test",
        smtp_from_email="onatowers@proton.me",
        sales_notification_email="onatowers@proton.me",
    )
    service = NotificationService(settings)
    status = service.configuration_status()
    assert status["ready"] is True
    assert settings.uses_resend_transport is True
    assert settings.effective_from_email == "sales@onatowers.com"
    assert service._from_header() == "ONA Towers <sales@onatowers.com>"
