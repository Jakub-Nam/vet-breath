"""FastAPI application entrypoint.

The app instance is assembled here: settings, routers, middleware. Keep this file
thin — domain logic lives in services, request/response shapes live in schemas, and
endpoints live in routers under `app/api/`. Run locally with:

    uv run uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
