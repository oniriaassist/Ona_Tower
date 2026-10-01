from fastapi import APIRouter

from app.api.routes import admin, analytics, cityview, content, enquiries, residences

api_router = APIRouter()
api_router.include_router(residences.router)
api_router.include_router(content.router)
api_router.include_router(enquiries.router)
api_router.include_router(analytics.router)
api_router.include_router(cityview.router)
api_router.include_router(admin.router)
