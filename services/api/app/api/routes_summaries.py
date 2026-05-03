"""Summary routes."""

from http import HTTPStatus

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import Settings, get_settings
from ..core.security import Principal, require_scope
from ..db.session import get_session
from ..schemas.jobs import JobCreateResponse
from ..schemas.summaries import SummaryJobCreateRequest, SummaryRequest, SummaryResponse
from ..services.cache_service import CacheService
from ..services.document_service import job_response
from ..services.model_client import ModelClient
from ..services.rate_limit_service import RateLimitService
from ..services.summary_service import SummaryService

router = APIRouter(prefix="/v1", tags=["summaries"])


@router.post("/summaries", response_model=SummaryResponse)
async def summarize(
    payload: SummaryRequest,
    principal: Principal = Depends(require_scope("summaries:write")),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SummaryResponse:
    """Run synchronous extractive summarization for short text."""
    service = SummaryService(
        settings,
        session,
        ModelClient(settings),
        CacheService(settings),
        RateLimitService(settings),
    )
    return SummaryResponse(**await service.summarize(principal, payload))


@router.post(
    "/summary-jobs",
    response_model=JobCreateResponse,
    status_code=HTTPStatus.ACCEPTED,
)
async def create_summary_job(
    payload: SummaryJobCreateRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    principal: Principal = Depends(require_scope("summaries:write")),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> JobCreateResponse:
    """Create an async summary job."""
    service = SummaryService(
        settings,
        session,
        ModelClient(settings),
        CacheService(settings),
        RateLimitService(settings),
    )
    job = await service.create_summary_job(principal, payload, idempotency_key)
    return JobCreateResponse(**job_response(job))
