from fastapi import APIRouter, Depends, Request, status

from app.core.config import Settings, get_settings
from app.repositories.base import BackendRepository
from app.repositories.dependencies import get_repository
from app.schemas.enquiry import EnquiryCreate, EnquiryCreated
from app.services.enquiry_service import EnquiryService
from app.services.rate_limit import rate_limiter

router = APIRouter(prefix="/enquiries", tags=["Enquiries"])


@router.post("", response_model=EnquiryCreated, status_code=status.HTTP_201_CREATED)
async def create_enquiry(
    payload: EnquiryCreate,
    request: Request,
    repository: BackendRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
):
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(
        f"enquiry:{client_ip}",
        limit=settings.enquiry_rate_limit_count,
        window_seconds=settings.enquiry_rate_limit_window_seconds,
    )

    service = EnquiryService(repository, settings)
    record = await service.submit(payload)

    # Honeypot submissions receive a generic success response without persistence.
    if record is None:
        return EnquiryCreated(reference_number="RECEIVED")

    result = service.last_notification_result
    message = (
        "Thank you. Your enquiry has been received and your City View link has been emailed to you."
        if result.customer_sent
        else "Thank you. Your enquiry has been received. Our sales team will follow up using the contact details you provided."
    )
    return EnquiryCreated(
        reference_number=record.reference_number,
        message=message,
        customer_email_sent=result.customer_sent,
        staff_email_sent=result.staff_sent,
    )
