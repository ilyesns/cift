from fastapi import APIRouter

from app.api.v1 import admin, admin_prayer, auth, health, prayer, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(prayer.router)
api_router.include_router(admin.router)
api_router.include_router(admin_prayer.router)
