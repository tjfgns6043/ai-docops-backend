"""Search and extractive RAG routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import Settings, get_settings
from ..core.security import Principal, require_scope
from ..db.session import get_session
from ..schemas.search import RagAnswerRequest, RagAnswerResponse, SearchRequest, SearchResponse
from ..services.cache_service import CacheService
from ..services.model_client import ModelClient
from ..services.rate_limit_service import RateLimitService
from ..services.search_service import SearchService

router = APIRouter(prefix="/v1", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(
    payload: SearchRequest,
    principal: Principal = Depends(require_scope("search:read")),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SearchResponse:
    """Run tenant-scoped semantic search."""
    service = SearchService(
        settings,
        session,
        ModelClient(settings),
        CacheService(settings),
        RateLimitService(settings),
    )
    return SearchResponse(**await service.search(principal, payload))


@router.post("/rag/answers", response_model=RagAnswerResponse)
async def rag_answer(
    payload: RagAnswerRequest,
    principal: Principal = Depends(require_scope("search:read")),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> RagAnswerResponse:
    """Return extractive RAG answer with citations."""
    service = SearchService(
        settings,
        session,
        ModelClient(settings),
        CacheService(settings),
        RateLimitService(settings),
    )
    return RagAnswerResponse(**await service.rag_answer(principal, payload))
