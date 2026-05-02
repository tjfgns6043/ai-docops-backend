"""Health and readiness routes."""

from fastapi import APIRouter, Request

from ..schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return process liveness."""
    return HealthResponse(status="ok", service="api")


@router.get("/ready", response_model=ReadyResponse)
async def ready(request: Request) -> ReadyResponse:
    """Return readiness.

    Dependency checks are introduced in later phases; for now the API process is ready
    once it can serve requests.
    """
    settings = request.app.state.settings
    return ReadyResponse(status="ready", service=settings.service_name, checks={})
