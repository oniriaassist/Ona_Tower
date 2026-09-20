import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings, is_production_runtime, production_configuration_errors
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware


settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_init_db and settings.app_env == "test" and not is_production_runtime(settings):
        from app.database.bootstrap import initialize_database
        initialize_database(create_schema=True)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.app_debug,
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", "Authorization", "X-Request-ID"],
)

app.include_router(health_router)
app.include_router(api_router, prefix=settings.api_prefix)


@app.middleware("http")
async def production_configuration_guard(request: Request, call_next):
    errors = production_configuration_errors(settings)
    if errors and request.url.path not in {"/health", "/health/config"}:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "ONA Towers API production configuration is invalid.",
                "code": "service_misconfigured",
            },
        )
    return await call_next(request)


@app.get("/")
async def root():
    return {
        "service": "ona-towers-api",
        "status": "ok",
        "docs": "/docs" if settings.app_env != "production" else None,
    }


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "The request contains invalid data.",
                "request_id": getattr(request.state, "request_id", None),
                "details": jsonable_encoder(exc.errors()),
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled application error")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected server error occurred.",
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )
