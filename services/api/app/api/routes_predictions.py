"""Prediction routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import Settings, get_settings
from ..core.security import Principal, require_scope
from ..db.session import get_session
from ..schemas.predictions import PredictionRequest, PredictionResponse
from ..services.cache_service import CacheService
from ..services.model_client import ModelClient
from ..services.prediction_service import PredictionService
from ..services.rate_limit_service import RateLimitService

router = APIRouter(prefix="/v1/predictions", tags=["predictions"])


@router.post("", response_model=PredictionResponse)
async def predict(
    payload: PredictionRequest,
    principal: Principal = Depends(require_scope("predictions:write")),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> PredictionResponse:
    """Run prototype embedding classification."""
    service = PredictionService(
        settings,
        session,
        ModelClient(settings),
        CacheService(settings),
        RateLimitService(settings),
    )
    return PredictionResponse(**await service.predict(principal, payload))
