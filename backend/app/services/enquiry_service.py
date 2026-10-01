import logging
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.config import Settings
from app.core.exceptions import DuplicateEnquiryError
from app.repositories.base import BackendRepository
from app.schemas.enquiry import EnquiryCreate, EnquiryRecord
from app.services.notification import NotificationResult, NotificationService
from app.services.sanitization import sanitize_plain_text

logger = logging.getLogger(__name__)


class EnquiryService:
    def __init__(self, repository: BackendRepository, settings: Settings):
        self.repository = repository
        self.settings = settings
        self.notifications = NotificationService(settings)
        self.last_notification_result = NotificationResult(provider=settings.effective_email_provider)

    async def submit(self, payload: EnquiryCreate) -> EnquiryRecord | None:
        # Honeypot: silently accept bot submissions but do not persist/notify.
        if payload.company_website.strip():
            logger.warning("Honeypot enquiry blocked")
            return None

        cleaned = payload.model_copy(
            update={
                "name": sanitize_plain_text(payload.name) or payload.name,
                "residence_interest": sanitize_plain_text(payload.residence_interest),
                "message": sanitize_plain_text(payload.message),
                "source": sanitize_plain_text(payload.source) or "website",
                "company_website": "",
            }
        )

        since = datetime.now(timezone.utc) - timedelta(seconds=self.settings.duplicate_enquiry_window_seconds)
        duplicate = await self.repository.has_recent_duplicate_enquiry(
            email=str(cleaned.email) if cleaned.email else None,
            phone=cleaned.phone,
            residence_interest=cleaned.residence_interest,
            since=since,
        )
        if duplicate:
            raise DuplicateEnquiryError()

        reference = self._make_reference_number()
        record = await self.repository.create_enquiry(cleaned, reference_number=reference)

        try:
            self.last_notification_result = self.notifications.send_enquiry_notifications(record)
        except Exception:
            # Notification failure must not lose a valid enquiry.
            logger.exception("Enquiry stored but notification failed")

        return record

    @staticmethod
    def _make_reference_number() -> str:
        date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
        suffix = uuid4().hex[:6].upper()
        return f"ONA-{date_part}-{suffix}"
