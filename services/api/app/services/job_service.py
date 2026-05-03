"""Job service."""

from http import HTTPStatus
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.errors import ApiError
from ..core.security import Principal
from ..db.models import Job
from ..db.repositories.jobs import JobRepository


class JobService:
    """Job lookup methods."""

    def __init__(self, session: AsyncSession) -> None:
        self.jobs = JobRepository(session)

    async def get_job(self, principal: Principal, job_id: UUID) -> Job:
        """Return a tenant-owned job."""
        try:
            job = await self.jobs.get_by_id(principal.tenant_id, job_id)
        except Exception as exc:
            raise ApiError(
                "DATABASE_UNAVAILABLE",
                "database is temporarily unavailable",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        if job is None:
            raise ApiError("RESOURCE_NOT_FOUND", "job not found", HTTPStatus.NOT_FOUND)
        return job


def serialize_job(job: Job) -> dict[str, object]:
    """Serialize a job for public responses."""
    error = None
    if job.error_code or job.error_message:
        error = {
            "code": job.error_code or "JOB_FAILED",
            "message": job.error_message or "job failed",
        }
    return {
        "job_id": job.id,
        "status": job.status,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "result": job.result,
        "error": error,
    }
