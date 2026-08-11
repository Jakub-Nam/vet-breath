"""Health-check router.

A router is one cohesive resource group: an `APIRouter` with its own prefix and tag,
explicit `response_model` on every operation. Mounted in `app/main.py`.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
