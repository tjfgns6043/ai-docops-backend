"""Health and readiness routes."""

import httpx
from fastapi import APIRouter, Request
from sqlalchemy import text

from ..db.session import make_session_factory
from ..schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return process liveness."""
    return HealthResponse(status="ok", service="api")


@router.get("/ready", response_model=ReadyResponse)
async def ready(request: Request) -> ReadyResponse:
    """Return readiness."""
    settings = request.app.state.settings
    if not settings.readiness_checks_enabled:
        return ReadyResponse(
            status="ready",
            service=settings.service_name,
            checks={"database": "skipped", "redis": "skipped", "model_server": "skipped"},
        )

    checks = {
        "database": await check_database(),
        "redis": await check_redis(settings.redis_url),
        "model_server": await check_model_server(settings.model_server_url),
    }
    status = "ready" if all(value == "ok" for value in checks.values()) else "not_ready"
    return ReadyResponse(status=status, service=settings.service_name, checks=checks)


async def check_database() -> str:
    """Check database connectivity."""
    try:
        session_factory = make_session_factory()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        return "unavailable"
    return "ok"


async def check_redis(redis_url: str) -> str:
    """Check Redis connectivity."""
    try:
        from redis.asyncio import Redis

        redis = Redis.from_url(redis_url)
        await redis.ping()
        await redis.aclose()
    except Exception:
        return "unavailable"
    return "ok"


async def check_model_server(model_server_url: str) -> str:
    """Check model server readiness."""
    try:
        async with httpx.AsyncClient(base_url=model_server_url, timeout=1.0) as client:
            response = await client.get("/ready")
            response.raise_for_status()
    except Exception:
        return "unavailable"
    return "ok"
