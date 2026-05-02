"""Inference request repository."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import InferenceRequest


def select_inference_requests_for_tenant(
    tenant_id: UUID,
) -> Select[tuple[InferenceRequest]]:
    """Build a tenant-scoped inference request lookup statement."""
    return select(InferenceRequest).where(InferenceRequest.tenant_id == tenant_id)


class InferenceRequestRepository:
    """Persistence methods for inference request audit rows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_tenant(self, tenant_id: UUID) -> list[InferenceRequest]:
        """List inference records for one tenant."""
        result = await self.session.execute(select_inference_requests_for_tenant(tenant_id))
        return list(result.scalars())
