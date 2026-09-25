from datetime import datetime, timezone
from uuid import uuid4

from app.repositories.base import BackendRepository
from app.schemas.content import Amenity, LocationPoint, SmartFeature
from app.schemas.enquiry import EnquiryCreate, EnquiryRecord
from app.schemas.residence import ResidenceDetail, ResidenceSummary


class InMemoryRepository(BackendRepository):
    """Development/test adapter only.

    This is intentionally not a database implementation. It lets the backend run before
    the database team's adapter is connected.
    """

    def __init__(self):
        self._residences = [
            ResidenceDetail(
                id="res-2br",
                slug="2-bedroom",
                name="2 Bedroom Residence",
                type="2 Bedroom",
                bedrooms=2,
                size_m2=202,
                short_description="Confirmed total area 202–206 sqm depending on tower and orientation.",
                display_order=1,
            ),
            ResidenceDetail(
                id="res-3br",
                slug="3-bedroom",
                name="3 Bedroom Residence",
                type="3 Bedroom",
                bedrooms=3,
                size_m2=236,
                short_description="Confirmed total area 236–240 sqm depending on tower and orientation.",
                display_order=2,
            ),
            ResidenceDetail(
                id="res-penthouse-3",
                slug="penthouse-3bed",
                name="03 Bedroom Signature Penthouse",
                type="Penthouse",
                bedrooms=3,
                size_m2=419,
                short_description=None,
                display_order=3,
            ),
            ResidenceDetail(
                id="res-penthouse-4",
                slug="penthouse-4bed",
                name="04 Bedroom Signature Penthouse",
                type="Penthouse",
                bedrooms=4,
                size_m2=487,
                short_description=None,
                display_order=4,
            ),
        ]
        self._amenities: list[Amenity] = []
        self._smart_features: list[SmartFeature] = []
        self._location_points: list[LocationPoint] = []
        self._enquiries: list[EnquiryRecord] = []

    async def list_residences(self) -> list[ResidenceSummary]:
        return [ResidenceSummary(**item.model_dump(exclude={"long_description", "features", "media", "floor_plans"})) for item in sorted(self._residences, key=lambda x: x.display_order)]

    async def get_residence_by_slug(self, slug: str) -> ResidenceDetail | None:
        return next((item for item in self._residences if item.slug == slug), None)

    async def list_amenities(self) -> list[Amenity]:
        return sorted([x for x in self._amenities if x.active], key=lambda x: x.display_order)

    async def list_smart_features(self) -> list[SmartFeature]:
        return sorted(self._smart_features, key=lambda x: x.display_order)

    async def list_location_points(self) -> list[LocationPoint]:
        return sorted(self._location_points, key=lambda x: x.display_order)

    async def create_enquiry(self, enquiry: EnquiryCreate, *, reference_number: str) -> EnquiryRecord:
        record = EnquiryRecord(
            id=str(uuid4()),
            reference_number=reference_number,
            name=enquiry.name,
            phone=enquiry.phone,
            email=enquiry.email,
            residence_interest=enquiry.residence_interest,
            enquiry_type=enquiry.enquiry_type,
            message=enquiry.message,
            consent=enquiry.consent,
            source=enquiry.source,
            status="new",
            created_at=datetime.now(timezone.utc),
        )
        self._enquiries.append(record)
        return record

    async def has_recent_duplicate_enquiry(self, *, email: str | None, phone: str, residence_interest: str | None, since: datetime) -> bool:
        for item in self._enquiries:
            same_person = (email and item.email and str(item.email).lower() == email.lower()) or item.phone == phone
            same_interest = item.residence_interest == residence_interest
            if same_person and same_interest and item.created_at >= since:
                return True
        return False
