"""Job API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    """Async job creation response."""

    job_id: UUID
    job_type: str
    status: str
    result_url: str


class JobResponse(BaseModel):
    """Async job status response."""

    job_id: UUID
    status: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    result: dict[str, object] | None
    error: dict[str, str] | None
