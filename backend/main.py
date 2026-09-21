"""Vercel Services entrypoint for the ONA Towers FastAPI backend."""

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse


try:
    from app.main import app as application
except Exception as exc:
    logging.getLogger("ona_towers.bootstrap").exception("ONA Towers backend bootstrap failed")
    _error_type = type(exc).__name__
    application = FastAPI(title="ONA Towers API", docs_url=None, redoc_url=None, openapi_url=None)

    @application.get("/health")
    async def bootstrap_health():
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "ona-towers-api",
                "stage": "bootstrap",
                "error_type": _error_type,
            },
        )

# Vercel statically checks for this binding at module scope.
app = application

__all__ = ["app"]
