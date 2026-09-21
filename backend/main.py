"""Vercel Services entrypoint for the ONA Towers FastAPI backend."""

import logging
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Services may import this file from the repository root rather than backend/.
backend_directory = str(Path(__file__).resolve().parent)
if backend_directory not in sys.path:
    sys.path.insert(0, backend_directory)

try:
    from app.main import app as application
except Exception as exc:
    logging.getLogger("ona_towers.bootstrap").exception("ONA Towers backend bootstrap failed")
    _error_type = type(exc).__name__
    _missing_module = exc.name if isinstance(exc, ModuleNotFoundError) else None
    application = FastAPI(title="ONA Towers API", docs_url=None, redoc_url=None, openapi_url=None)

    @application.get("/health")
    @application.get("/health/config")
    @application.get("/health/database")
    async def bootstrap_health():
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "ona-towers-api",
                "stage": "bootstrap",
                "error_type": _error_type,
                "missing_module": _missing_module,
            },
        )

    @application.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def unavailable_api(path: str):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "ONA Towers API could not start. Please try again later.",
                "code": "service_bootstrap_failed",
            },
        )

# Vercel statically checks for this binding at module scope.
app = application

__all__ = ["app"]
