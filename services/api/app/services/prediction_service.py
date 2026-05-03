"""Prediction service."""

from time import perf_counter

from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.ids import new_request_id

from ..core.config import Settings
from ..core.security import Principal
from ..schemas.predictions import PredictionRequest
from .cache_service import CacheService, build_cache_key, hash_payload
from .model_client import ModelClient
from .rate_limit_service import RateLimitService
from .summary_service import SummaryService


class PredictionService:
    """Prototype classification workflow."""

    def __init__(
        self,
        settings: Settings,
        session: AsyncSession,
        model_client: ModelClient,
        cache: CacheService,
        rate_limits: RateLimitService,
    ) -> None:
        self.settings = settings
        self.session = session
        self.model_client = model_client
        self.cache = cache
        self.rate_limits = rate_limits
        self.summary_service = SummaryService(settings, session, model_client, cache, rate_limits)

    async def predict(self, principal: Principal, payload: PredictionRequest) -> dict[str, object]:
        """Return prototype classification predictions."""
        await self.summary_service._check_rate_limit(principal, "predictions")
        input_hash = hash_payload(payload.model_dump())
        cache_key = build_cache_key(
            self.settings.app_env,
            str(principal.tenant_id),
            "prediction",
            self.settings.model_version,
            self.settings.preprocess_version,
            input_hash,
        )
        cached = await self.cache.get_json(cache_key)
        if cached.value:
            cached.value["cached"] = True
            return cached.value

        started_at = perf_counter()
        model_response = await self.model_client.classify(
            payload.text,
            [label.model_dump() for label in payload.labels],
            payload.top_k,
        )
        elapsed_ms = (perf_counter() - started_at) * 1000
        response = {
            "request_id": new_request_id(),
            "model_version": str(model_response["model_version"]),
            "predictions": list(model_response["predictions"]),
            "elapsed_ms": float(model_response.get("elapsed_ms", elapsed_ms)),
            "cached": False,
        }
        await self.cache.set_json(cache_key, response, self.settings.cache_ttl_prediction_seconds)
        await self.summary_service._record_inference(
            principal,
            "prediction",
            input_hash,
            {
                "model_version": response["model_version"],
                "preprocess_version": self.settings.preprocess_version,
                "cached": False,
            },
            elapsed_ms,
        )
        return response
