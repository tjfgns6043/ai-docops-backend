"""API authentication and authorization dependencies."""

from dataclasses import dataclass
from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.hashing import hash_api_key

from ..db.repositories.api_keys import ApiKeyRepository
from ..db.session import get_session
from .config import Settings, get_settings
from .errors import ApiError


@dataclass(frozen=True)
class Principal:
    """Authenticated tenant principal."""

    tenant_id: UUID
    owner_id: UUID
    scopes: frozenset[str]


def dev_principal(settings: Settings) -> Principal:
    """Return the local development principal."""
    return Principal(
        tenant_id=UUID(settings.dev_tenant_id),
        owner_id=UUID(settings.dev_owner_id),
        scopes=frozenset(
            {
                "documents:write",
                "documents:read",
                "summaries:write",
                "predictions:write",
                "search:read",
                "jobs:read",
            }
        ),
    )


async def get_current_principal(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> Principal:
    """Authenticate an API key and return tenant context."""
    if not x_api_key:
        raise ApiError("AUTH_REQUIRED", "X-API-Key header is required", HTTPStatus.UNAUTHORIZED)

    key_hash = hash_api_key(x_api_key)
    try:
        api_key = await ApiKeyRepository(session).get_active_by_hash(key_hash)
    except Exception as exc:
        if settings.allow_dev_auth_fallback and x_api_key == settings.dev_api_key:
            return dev_principal(settings)
        raise ApiError(
            "DATABASE_UNAVAILABLE",
            "database is temporarily unavailable",
            HTTPStatus.SERVICE_UNAVAILABLE,
        ) from exc

    if api_key is None:
        if settings.allow_dev_auth_fallback and x_api_key == settings.dev_api_key:
            return dev_principal(settings)
        raise ApiError("AUTH_INVALID", "API key is invalid", HTTPStatus.UNAUTHORIZED)

    return Principal(
        tenant_id=api_key.tenant_id,
        owner_id=api_key.owner_id,
        scopes=frozenset(api_key.scopes),
    )


def require_scope(scope: str):
    """Return a dependency that requires one scope."""

    async def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if scope not in principal.scopes:
            raise ApiError("FORBIDDEN", "scope is required", HTTPStatus.FORBIDDEN)
        return principal

    return dependency
