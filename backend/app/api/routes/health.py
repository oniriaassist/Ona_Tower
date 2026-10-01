import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import inspect, text

from app.core.config import (
    get_settings,
    production_configuration_errors,
    production_configuration_warnings,
)
from app.services.notification import NotificationService


router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ona-towers-api"}


@router.get("/health/config")
async def configuration_health():
    try:
        settings = get_settings()
        errors = production_configuration_errors(settings)
        warnings = production_configuration_warnings(settings)
        email_status = NotificationService(settings).configuration_status()
    except Exception as exc:
        logger.exception("Production configuration check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "misconfigured", "error_type": type(exc).__name__},
        ) from exc

    if errors:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "misconfigured",
                "error_type": "RuntimeError",
                "errors": errors,
            },
        )

    return {
        "status": "ok",
        "environment": settings.app_env,
        "database_configured": bool(settings.sqlalchemy_database_url),
        "database_ssl_required": "sslmode=require" in settings.sqlalchemy_database_url.lower(),
        "email": {
            "enabled": email_status["enabled"],
            "ready": email_status["ready"],
            "provider": email_status["provider"],
            "from_configured": email_status["from_configured"],
            "from_domain": email_status.get("from_domain", ""),
            "resend_domain_match": email_status.get("resend_domain_match", True),
            "staff_recipient_configured": email_status["staff_recipient_configured"],
            "cityview_url_configured": email_status["cityview_url_configured"],
            "cityview_url": email_status.get("cityview_url", settings.cityview_public_url),
        },
        "warnings": warnings,
    }


@router.get("/health/database")
def database_health():
    required_tables = {
        "residences",
        "residence_media",
        "floor_plans",
        "amenities",
        "smart_features",
        "location_points",
        "enquiries",
        "admin_team_members",
        "admin_settings",
        "site_visits",
    }

    try:
        from app.database.session import get_engine

        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            existing_tables = set(inspect(connection).get_table_names())
            missing_tables = sorted(required_tables - existing_tables)
            alembic_revision = None
            if "alembic_version" in existing_tables:
                alembic_revision = connection.execute(
                    text("SELECT version_num FROM alembic_version LIMIT 1")
                ).scalar()

            residence_count = 0
            admin_count = 0
            if "residences" in existing_tables:
                residence_count = int(connection.execute(text("SELECT COUNT(*) FROM residences")).scalar() or 0)
            if "admin_team_members" in existing_tables:
                admin_count = int(
                    connection.execute(
                        text("SELECT COUNT(*) FROM admin_team_members WHERE active = true")
                    ).scalar()
                    or 0
                )

    except Exception as exc:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable",
        ) from exc

    if missing_tables:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "schema_incomplete",
                "database": "connected",
                "missing_tables": missing_tables,
                "alembic_revision": alembic_revision,
            },
        )

    return {
        "status": "ok",
        "service": "ona-towers-api",
        "database": "connected",
        "schema": "ready",
        "alembic_revision": alembic_revision,
        "residence_count": residence_count,
        "active_admin_count": admin_count,
    }
