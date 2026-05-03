"""Summary service."""

from http import HTTPStatus
from time import perf_counter
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.ids import new_request_id
from libs.common.status import JOB_QUEUED

from ..core.config import Settings
from ..core.errors import ApiError
from ..core.security import Principal
from ..db.models import InferenceRequest, Job
from ..db.repositories.inference_requests import InferenceRequestRepository
from ..db.repositories.jobs import JobRepository
from ..schemas.summaries import SummaryJobCreateRequest, SummaryRequest
from .cache_service import CacheService, build_cache_key, hash_payload
from .model_client import ModelClient
from .rate_limit_service import RateLimiterUnavailable, RateLimitExceeded, RateLimitService


class SummaryService:
    """Synchronous and async summary workflow methods."""

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
        self.inference_requests = InferenceRequestRepository(session)
        self.jobs = JobRepository(session)

    async def summarize(self, principal: Principal, payload: SummaryRequest) -> dict[str, object]:
        """Return a synchronous extractive summary."""
        await self._check_rate_limit(principal, "summaries")
        input_hash = hash_payload(payload.model_dump())
        cache_key = build_cache_key(
            self.settings.app_env,
            str(principal.tenant_id),
            "summary",
            payload.model_version,
            self.settings.preprocess_version,
            input_hash,
        )
        cached = await self.cache.get_json(cache_key)
        if cached.value:
            cached.value["cached"] = True
            return cached.value

        started_at = perf_counter()
        model_response = await self.model_client.summarize(
            payload.text,
            payload.max_sentences,
            payload.language,
        )
        elapsed_ms = (perf_counter() - started_at) * 1000
        response = {
            "request_id": new_request_id(),
            "summary": str(model_response["summary"]),
            "model_version": str(model_response["model_version"]),
            "preprocess_version": str(model_response["preprocess_version"]),
            "cached": False,
            "elapsed_ms": float(model_response.get("elapsed_ms", elapsed_ms)),
        }
        await self.cache.set_json(cache_key, response, self.settings.cache_ttl_summary_seconds)
        await self._record_inference(principal, "summary", input_hash, response, elapsed_ms)
        return response

    async def create_summary_job(
        self,
        principal: Principal,
        payload: SummaryJobCreateRequest,
        idempotency_key: str | None,
    ) -> Job:
        """Create a queued summary job."""
        await self._check_rate_limit(principal, "job_create")
        request_hash = hash_payload(payload.model_dump(mode="json"))
        try:
            if idempotency_key:
                existing = await self.jobs.get_by_idempotency_key(
                    principal.tenant_id,
                    idempotency_key,
                )
                if existing:
                    return existing
            job = Job(
                id=uuid4(),
                tenant_id=principal.tenant_id,
                owner_id=principal.owner_id,
                job_type="summarize_document",
                status=JOB_QUEUED,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                payload=payload.model_dump(mode="json", exclude_none=True),
            )
            created = await self.jobs.add(job)
            await self.session.commit()
            enqueue_summary_document(created.id)
            return created
        except Exception as exc:
            await self.session.rollback()
            raise ApiError(
                "DATABASE_UNAVAILABLE",
                "database is temporarily unavailable",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc

    async def _record_inference(
        self,
        principal: Principal,
        request_type: str,
        input_hash: str,
        response: dict[str, object],
        elapsed_ms: float,
    ) -> None:
        try:
            await self.inference_requests.add(
                InferenceRequest(
                    tenant_id=principal.tenant_id,
                    owner_id=principal.owner_id,
                    request_type=request_type,
                    input_hash=input_hash,
                    model_version=str(response["model_version"]),
                    preprocess_version=str(response["preprocess_version"]),
                    status="completed",
                    cached=bool(response["cached"]),
                    latency_ms=elapsed_ms,
                )
            )
            await self.session.commit()
        except Exception:
            await self.session.rollback()

    async def _check_rate_limit(self, principal: Principal, operation: str) -> None:
        try:
            await self.rate_limits.check(principal.tenant_id, operation)
        except RateLimitExceeded as exc:
            raise ApiError(
                "RATE_LIMIT_EXCEEDED",
                "rate limit exceeded",
                HTTPStatus.TOO_MANY_REQUESTS,
            ) from exc
        except RateLimiterUnavailable as exc:
            raise ApiError(
                "RATE_LIMITER_UNAVAILABLE",
                "rate limiter is temporarily unavailable",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc


def enqueue_summary_document(job_id: object) -> None:
    """Enqueue a summary task if Celery is available."""
    try:
        from services.worker.app.tasks.summarize_document import summarize_document_task

        summarize_document_task.delay(str(job_id))
    except Exception:
        return
