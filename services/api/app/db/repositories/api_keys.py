"""API key repository."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ApiKey


def select_active_api_key_by_hash(key_hash: str) -> Select[tuple[ApiKey]]:
    """Build a lookup statement for an active hashed API key."""
    return select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.status == "active")


class ApiKeyRepository:
    """Persistence methods for API keys."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active_by_hash(self, key_hash: str) -> ApiKey | None:
        """Return an active API key by hash."""
        result = await self.session.execute(select_active_api_key_by_hash(key_hash))
        return result.scalar_one_or_none()

    async def belongs_to_tenant(self, key_id: UUID, tenant_id: UUID) -> bool:
        """Return whether an API key belongs to a tenant."""
        result = await self.session.execute(
            select(ApiKey.id).where(ApiKey.id == key_id, ApiKey.tenant_id == tenant_id),
        )
        return result.scalar_one_or_none() is not None
