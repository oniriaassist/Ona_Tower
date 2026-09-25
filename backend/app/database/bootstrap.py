import logging

from sqlalchemy import select

from app.core.config import get_settings, validate_production_settings
from app.core.passwords import hash_password
from app.database.base import Base
from app.database.models import (
    AdminTeamMember, Amenity, FloorPlan, LocationPoint, Residence,
    ResidenceMedia, SmartFeature,
)
from app.database.session import SessionLocal, get_engine

logger = logging.getLogger(__name__)

RESIDENCES = [
    {
        "slug": "2-bedroom",
        "name": "02 Bedroom Residence",
        "type": "2 Bedroom",
        "bedrooms": 2,
        "size_m2": 202,
        "short_description": "Two-bedroom residence; confirmed total area varies from 202 to 206 sqm by tower and orientation.",
        "features": ["2 bedrooms", "202–206 sqm confirmed total-area range", "2 units per typical residential floor"],
        "display_order": 1,
        "status": "active",
        "cover_image": "/ona-assets/canva/plan_2_bedroom_residential.png",
    },
    {
        "slug": "3-bedroom",
        "name": "03 Bedroom Residence",
        "type": "3 Bedroom",
        "bedrooms": 3,
        "size_m2": 236,
        "short_description": "Three-bedroom residence; confirmed total area varies from 236 to 240 sqm by tower and orientation.",
        "features": ["3 bedrooms", "236–240 sqm confirmed total-area range", "2 units per typical residential floor"],
        "display_order": 2,
        "status": "active",
        "cover_image": "/ona-assets/canva/plan_3_bedroom_residential.png",
    },
    {
        "slug": "penthouse-3bed",
        "name": "03 Bedroom Signature Penthouse",
        "type": "Penthouse",
        "bedrooms": 3,
        "size_m2": 419,
        "short_description": "Three-bedroom residence on the penthouse level.",
        "features": ["3 bedrooms", "419 sqm Tower A · 423 sqm Tower B", "Penthouse level"],
        "display_order": 3,
        "status": "active",
        "cover_image": "/ona-assets/canva/plan_3_bedroom_penthouse.png",
    },
    {
        "slug": "penthouse-4bed",
        "name": "04 Bedroom Signature Penthouse",
        "type": "Penthouse",
        "bedrooms": 4,
        "size_m2": 487,
        "short_description": "Four-bedroom residence on the penthouse level.",
        "features": ["4 bedrooms", "487 sqm Tower A · 491 sqm Tower B", "Penthouse level"],
        "display_order": 4,
        "status": "active",
        "cover_image": "/ona-assets/canva/plan_4_bedroom_penthouse.png",
    },
]

FLOOR_PLANS = [
    {
        "residence_slug": "2-bedroom",
        "plan_name": "02 Bedroom Residence Plan",
        "file_url": "/ona-assets/canva/plan_2_bedroom_residential.png",
        "preview_image_url": "/ona-assets/canva/plan_2_bedroom_residential.png",
    },
    {
        "residence_slug": "3-bedroom",
        "plan_name": "03 Bedroom Residence Plan",
        "file_url": "/ona-assets/canva/plan_3_bedroom_residential.png",
        "preview_image_url": "/ona-assets/canva/plan_3_bedroom_residential.png",
    },
    {
        "residence_slug": "penthouse-3bed",
        "plan_name": "03 Bedroom Signature Penthouse Plan",
        "file_url": "/ona-assets/canva/plan_3_bedroom_penthouse.png",
        "preview_image_url": "/ona-assets/canva/plan_3_bedroom_penthouse.png",
    },
    {
        "residence_slug": "penthouse-4bed",
        "plan_name": "04 Bedroom Signature Penthouse Plan",
        "file_url": "/ona-assets/canva/plan_4_bedroom_penthouse.png",
        "preview_image_url": "/ona-assets/canva/plan_4_bedroom_penthouse.png",
    },
]

RESIDENCE_MEDIA = [
    {
        "residence_slug": "2-bedroom",
        "media_type": "image",
        "url": "/ona-assets/canva/plan_2_bedroom_residential.png",
        "alt_text": "Two-bedroom residence project drawing",
        "display_order": 1,
    },
    {
        "residence_slug": "3-bedroom",
        "media_type": "image",
        "url": "/ona-assets/canva/plan_3_bedroom_residential.png",
        "alt_text": "Three-bedroom residence project drawing",
        "display_order": 1,
    },
    {
        "residence_slug": "penthouse-3bed",
        "media_type": "image",
        "url": "/ona-assets/canva/plan_3_bedroom_penthouse.png",
        "alt_text": "Three-bedroom signature penthouse project drawing",
        "display_order": 1,
    },
    {
        "residence_slug": "penthouse-4bed",
        "media_type": "image",
        "url": "/ona-assets/canva/plan_4_bedroom_penthouse.png",
        "alt_text": "Four-bedroom signature penthouse project drawing",
        "display_order": 1,
    },
]

AMENITIES = [
    {"name": "Pool", "category": "Lifestyle", "description": "Pool on the terrace / lifestyle level.", "display_order": 1},
    {"name": "Restaurant & Outdoor Dining", "category": "Lifestyle", "description": "Restaurant and outdoor restaurant on the terrace / lifestyle level.", "display_order": 2},
    {"name": "Gym", "category": "Lifestyle", "description": "Gym on the terrace / lifestyle level.", "display_order": 3},
    {"name": "Coffee & Work Area", "category": "Commercial", "description": "Coffee / work area on the ground floor.", "display_order": 4},
    {"name": "Supermarket", "category": "Commercial", "description": "Supermarket on the ground floor.", "display_order": 5},
]

SMART_FEATURES = [
    {"name": "Integrated mixed-use living", "benefit_statement": "Residences, lifestyle facilities and commercial functions are brought together within one development.", "display_order": 1},
]

LOCATION_POINTS = [
    {"name": "ZNZ Airport", "category": "Connection", "distance_or_travel_note": "Approx. 2 min", "display_order": 1},
    {"name": "Stone Town", "category": "Connection", "distance_or_travel_note": "Approx. 7 min", "display_order": 2},
    {"name": "Ferry Port", "category": "Connection", "distance_or_travel_note": "Approx. 10 min", "display_order": 3},
    {"name": "Fumba", "category": "Connection", "distance_or_travel_note": "Approx. 15 min", "display_order": 4},
]


def _ensure_default_admin(db) -> None:
    settings = get_settings()
    email = settings.admin_email.strip().lower()
    member = db.scalar(select(AdminTeamMember).where(AdminTeamMember.email == email))
    if member is None:
        member = AdminTeamMember(
            name=settings.admin_name.strip(),
            email=email,
            role=settings.admin_role.strip(),
            department=settings.admin_department.strip() or None,
            password_hash=hash_password(settings.admin_password),
            is_super_admin=True,
            active=True,
        )
        db.add(member)
    elif not member.password_hash:
        # This safely upgrades the original admin workspace where team members
        # were assignment records rather than login accounts.
        member.password_hash = hash_password(settings.admin_password)
        member.is_super_admin = True
        member.active = True
        db.add(member)


def _seed_if_missing(db, model, rows, key: str = "name") -> None:
    for row in rows:
        value = row[key]
        if db.scalar(select(model).where(getattr(model, key) == value)) is None:
            db.add(model(**row))


def initialize_database(*, create_schema: bool = False) -> None:
    """Seed verified baseline content; schema creation is reserved for tests.

    Development and production schemas are owned by Alembic. Keeping runtime
    startup from calling ``create_all`` prevents the database from getting ahead
    of the Alembic version table and eliminates duplicate-column migration drift.
    """
    validate_production_settings(get_settings())
    if create_schema:
        Base.metadata.create_all(bind=get_engine())
    with SessionLocal(bind=get_engine()) as db:
        _seed_if_missing(db, Residence, RESIDENCES, key="slug")
        db.flush()

        for row in FLOOR_PLANS:
            residence = db.scalar(select(Residence).where(Residence.slug == row["residence_slug"]))
            if residence is None:
                continue
            existing = db.scalar(
                select(FloorPlan).where(
                    FloorPlan.residence_id == residence.id,
                    FloorPlan.plan_name == row["plan_name"],
                )
            )
            if existing is None:
                db.add(
                    FloorPlan(
                        residence_id=residence.id,
                        plan_name=row["plan_name"],
                        file_url=row["file_url"],
                        preview_image_url=row["preview_image_url"],
                    )
                )

        for row in RESIDENCE_MEDIA:
            residence = db.scalar(select(Residence).where(Residence.slug == row["residence_slug"]))
            if residence is None:
                continue
            existing = db.scalar(
                select(ResidenceMedia).where(
                    ResidenceMedia.residence_id == residence.id,
                    ResidenceMedia.url == row["url"],
                )
            )
            if existing is None:
                db.add(
                    ResidenceMedia(
                        residence_id=residence.id,
                        media_type=row["media_type"],
                        url=row["url"],
                        alt_text=row["alt_text"],
                        display_order=row["display_order"],
                    )
                )

        _seed_if_missing(db, Amenity, AMENITIES)
        _seed_if_missing(db, SmartFeature, SMART_FEATURES)
        _seed_if_missing(db, LocationPoint, LOCATION_POINTS)
        _ensure_default_admin(db)
        db.commit()
    logger.info("Database seed is ready")
