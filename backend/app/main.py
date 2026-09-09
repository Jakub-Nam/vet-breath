"""FastAPI application entrypoint.

The app instance is assembled here: settings, routers, middleware. Keep this file
thin — domain logic lives in services, request/response shapes live in schemas, and
endpoints live in routers under `app/api/`. Run locally with:

    uv run uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.dogs import router as dogs_router
from app.api.health import router as health_router
from app.api.readings import router as readings_router
from app.api.vets import router as vets_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    # Also allow Cloudflare Pages preview branches (e.g. trusted-types.vet-breath.pages.dev),
    # so the XSS-defense preview shares this backend without a per-origin config change.
    allow_origin_regex=r"https://[a-z0-9-]+\.vet-breath\.pages\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(vets_router)
app.include_router(dogs_router)
app.include_router(readings_router)
