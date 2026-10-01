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
        email_enabled=True,
        email_provider="resend",
        resend_api_key="re_test",
        smtp_from_email="sales@onatowers.com",
        sales_notification_email="sales@onatowers.com",
        cityview_url="https://www.onatowers.com/cityview",
    )
    status = NotificationService(settings).configuration_status()
    assert status["ready"] is True
    assert status["provider"] == "resend"


def test_customer_and_staff_notifications_are_independent(monkeypatch):
    settings = Settings(
        email_enabled=True,
        email_provider="resend",
        resend_api_key="re_test",
        smtp_from_email="sales@onatowers.com",
        sales_notification_email="sales@onatowers.com",
        cityview_url="https://www.onatowers.com/cityview",
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
    assert "https://www.onatowers.com/cityview" in delivered[0][1]
    assert delivered[0][2] == "ona-customer/ONA-20261001-ABC123"


def test_email_disabled_reports_not_ready():
    settings = Settings(
        email_enabled=False,
        smtp_from_email="sales@onatowers.com",
        cityview_url="https://www.onatowers.com/cityview",
    )
    status = NotificationService(settings).configuration_status()
    assert status["enabled"] is False
    assert status["ready"] is False
    assert any("disabled" in issue.lower() for issue in status["issues"])
