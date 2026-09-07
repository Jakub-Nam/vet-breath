"""Health-check router.

A router is one cohesive resource group: an `APIRouter` with its own prefix and tag,
explicit `response_model` on every operation. Mounted in `app/main.py`.
"""

from importlib.metadata import PackageNotFoundError, version

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])

try:
    # The distribution name from pyproject.toml. `uv sync` installs the project
    # (editable), so this resolves in dev and in the built image alike.
    _VERSION = version("vet-breath")
except PackageNotFoundError:  # pragma: no cover - only when running from an uninstalled tree
    _VERSION = "unknown"


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=_VERSION)
