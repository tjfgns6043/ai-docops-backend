"""Job repository."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Job


def select_job_by_id(tenant_id: UUID, job_id: UUID) -> Select[tuple[Job]]:
    """Build a tenant-scoped job lookup statement."""
    return select(Job).where(Job.tenant_id == tenant_id, Job.id == job_id)


def select_job_by_idempotency_key(tenant_id: UUID, key: str) -> Select[tuple[Job]]:
    """Build a tenant-scoped idempotency lookup for jobs."""
    return select(Job).where(Job.tenant_id == tenant_id, Job.idempotency_key == key)


class JobRepository:
    """Persistence methods for jobs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, tenant_id: UUID, job_id: UUID) -> Job | None:
        """Return a tenant-owned job by ID."""
        result = await self.session.execute(select_job_by_id(tenant_id, job_id))
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, tenant_id: UUID, key: str) -> Job | None:
        """Return a tenant-owned job by idempotency key."""
        result = await self.session.execute(select_job_by_idempotency_key(tenant_id, key))
        return result.scalar_one_or_none()

    async def add(self, job: Job) -> Job:
        """Add a job."""
        self.session.add(job)
        await self.session.flush()
        await self.session.refresh(job)
        return job
