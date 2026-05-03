"""Search and extractive RAG service."""

from http import HTTPStatus
from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.ids import new_request_id
from services.model_server.app.services.text_processing import split_sentences

from ..core.config import Settings
from ..core.errors import ApiError
from ..core.security import Principal
from ..schemas.search import RagAnswerRequest, SearchRequest, SearchResult
from .cache_service import CacheService, build_cache_key, hash_payload
from .model_client import ModelClient
from .rate_limit_service import RateLimitService
from .summary_service import SummaryService


def to_pgvector_literal(vector: list[float]) -> str:
    """Convert a vector to pgvector literal syntax."""
    return "[" + ",".join(f"{value:.8f}" for value in vector) + "]"


class SearchService:
    """Semantic search and extractive RAG workflow."""

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

    async def search(self, principal: Principal, payload: SearchRequest) -> dict[str, object]:
        """Run tenant-scoped vector search."""
        await self.summary_service._check_rate_limit(principal, "search")
        started_at = perf_counter()
        input_hash = hash_payload(payload.model_dump(mode="json"))
        cache_key = build_cache_key(
            self.settings.app_env,
            str(principal.tenant_id),
            "search",
            self.settings.model_version,
            self.settings.preprocess_version,
            input_hash,
        )
        cached = await self.cache.get_json(cache_key)
        if cached.value:
            return cached.value

        embedding_response = await self.model_client.embed([payload.query], normalize=True)
        embedding = list(embedding_response["embeddings"])[0]
        results = await self._search_chunks(
            principal.tenant_id,
            list(map(float, embedding)),
            payload.top_k,
            payload.document_ids,
        )
        response = {
            "request_id": new_request_id(),
            "query": payload.query,
            "results": [result.model_dump(mode="json") for result in results],
            "elapsed_ms": (perf_counter() - started_at) * 1000,
        }
        await self.cache.set_json(cache_key, response, self.settings.cache_ttl_search_seconds)
        return response

    async def rag_answer(
        self,
        principal: Principal,
        payload: RagAnswerRequest,
    ) -> dict[str, object]:
        """Return an extractive answer with citations."""
        started_at = perf_counter()
        search_response = await self.search(
            principal,
            SearchRequest(query=payload.question, top_k=payload.top_k),
        )
        results = [SearchResult(**result) for result in search_response["results"]]
        answer_sentences = self._select_answer_sentences(results, payload.max_answer_sentences)
        citations = [
            {
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
                "chunk_index": result.chunk_index,
                "score": result.score,
            }
            for result in results[: min(len(results), payload.max_answer_sentences)]
        ]
        return {
            "request_id": new_request_id(),
            "answer_type": "extractive",
            "answer": " ".join(answer_sentences),
            "citations": citations,
            "model_version": self.settings.model_version,
            "elapsed_ms": (perf_counter() - started_at) * 1000,
        }

    async def _search_chunks(
        self,
        tenant_id: UUID,
        embedding: list[float],
        top_k: int,
        document_ids: list[UUID] | None,
    ) -> list[SearchResult]:
        where_document = ""
        params: dict[str, Any] = {
            "tenant_id": str(tenant_id),
            "query_embedding": to_pgvector_literal(embedding),
            "top_k": top_k,
        }
        if document_ids:
            where_document = "AND document_id = ANY(:document_ids)"
            params["document_ids"] = [str(document_id) for document_id in document_ids]
        statement = text(
            f"""
            SELECT id, document_id, chunk_index, text,
                   1 - (embedding <=> CAST(:query_embedding AS vector)) AS score,
                   metadata
            FROM document_chunks
            WHERE tenant_id = :tenant_id
              {where_document}
            ORDER BY embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
            """
        )
        try:
            rows = (await self.session.execute(statement, params)).mappings().all()
        except Exception as exc:
            raise ApiError(
                "DATABASE_UNAVAILABLE",
                "database is temporarily unavailable",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        return [
            SearchResult(
                chunk_id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                score=float(row["score"]),
                text=row["text"],
                metadata=dict(row["metadata"] or {}),
            )
            for row in rows
        ]

    def _select_answer_sentences(
        self,
        results: list[SearchResult],
        max_sentences: int,
    ) -> list[str]:
        selected: list[str] = []
        seen: set[str] = set()
        for result in results:
            for sentence in split_sentences(result.text):
                key = sentence.casefold().strip()
                if key in seen:
                    continue
                seen.add(key)
                selected.append(sentence)
                if len(selected) >= max_sentences:
                    return selected
        return selected
