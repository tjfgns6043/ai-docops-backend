"""Job routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import Principal, require_scope
from ..db.session import get_session
from ..schemas.jobs import JobResponse
from ..services.job_service import JobService, serialize_job

router = APIRouter(prefix="/v1", tags=["jobs"])


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    principal: Principal = Depends(require_scope("jobs:read")),
    session: AsyncSession = Depends(get_session),
) -> JobResponse:
    """Get a tenant-owned job."""
    job = await JobService(session).get_job(principal, job_id)
    return JobResponse(**serialize_job(job))


@router.get("/summary-jobs/{job_id}", response_model=JobResponse)
async def get_summary_job(
    job_id: UUID,
    principal: Principal = Depends(require_scope("jobs:read")),
    session: AsyncSession = Depends(get_session),
) -> JobResponse:
    """Get a tenant-owned summary job."""
    job = await JobService(session).get_job(principal, job_id)
    return JobResponse(**serialize_job(job))
