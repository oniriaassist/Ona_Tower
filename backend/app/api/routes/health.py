from fastapi import APIRouter

from app.core.config import (
    get_settings,
    production_configuration_errors,
    runtime_configuration_snapshot,
)


router = APIRouter(
    tags=["Health"],
)


@router.get(
    "/health",
    summary="API health check",
)
async def health():
    settings = (
        get_settings()
    )

    errors = (
        production_configuration_errors(
            settings
        )
    )

    return {
        "service":
            "ona-towers-api",

        "status":
            (
                "ok"
                if not errors
                else "misconfigured"
            ),

        "environment":
            settings.app_env,

        "production_config_valid":
            len(errors) == 0,
    }


@router.get(
    "/health/config",
    summary=(
        "Safe production "
        "configuration status"
    ),
)
async def health_config():
    settings = (
        get_settings()
    )

    snapshot = (
        runtime_configuration_snapshot(
            settings
        )
    )

    return {
        "service":
            "ona-towers-api",

        "status":
            (
                "ok"
                if snapshot[
                    "production_configuration_valid"
                ]
                else
                "misconfigured"
            ),

        "configuration":
            snapshot,
    }