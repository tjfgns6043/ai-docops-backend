"""Idempotency key repository."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import IdempotencyKey


def select_idempotency_key(tenant_id: UUID, key: str) -> Select[tuple[IdempotencyKey]]:
    """Build a tenant-scoped idempotency lookup statement."""
    return select(IdempotencyKey).where(
        IdempotencyKey.tenant_id == tenant_id,
        IdempotencyKey.key == key,
    )


class IdempotencyRepository:
    """Persistence methods for idempotency records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, tenant_id: UUID, key: str) -> IdempotencyKey | None:
        """Return a tenant-owned idempotency record."""
        result = await self.session.execute(select_idempotency_key(tenant_id, key))
        return result.scalar_one_or_none()
