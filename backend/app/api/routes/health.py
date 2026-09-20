import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.core.config import (
    get_settings,
    production_configuration_errors,
)


router = APIRouter(tags=["Health"])

logger = logging.getLogger(__name__)


@router.get("/health")
async def health():
    """
    Pure liveness endpoint.

    Must not require PostgreSQL or Supabase to answer.
    """
    return {
        "status": "ok",
        "service": "ona-towers-api",
    }


@router.get("/health/config")
async def configuration_health():
    settings = get_settings()
    errors = production_configuration_errors(settings)

    if errors:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "misconfigured",
                "errors": errors,
            },
        )

    return {
        "status": "ok",
        "environment": settings.app_env,
        "database_configured": True,
    }


@router.get("/health/database")
def database_health():
    try:
        from app.database.session import get_engine

        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))

    except Exception as exc:
        logger.exception("Database health check failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable",
        ) from exc

    return {
        "status": "ok",
        "service": "ona-towers-api",
        "database": "connected",
    }
