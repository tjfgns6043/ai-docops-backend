"""Search and RAG API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Semantic search request."""

    query: str = Field(min_length=1, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[UUID] | None = None


class SearchResult(BaseModel):
    """One search result."""

    chunk_id: UUID
    document_id: UUID
    chunk_index: int
    score: float
    text: str
    metadata: dict[str, object]


class SearchResponse(BaseModel):
    """Semantic search response."""

    request_id: str
    query: str
    results: list[SearchResult]
    elapsed_ms: float


class RagAnswerRequest(BaseModel):
    """Extractive RAG answer request."""

    question: str = Field(min_length=1, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=20)
    max_answer_sentences: int = Field(default=4, ge=1, le=10)


class Citation(BaseModel):
    """Answer citation."""

    chunk_id: UUID
    document_id: UUID
    chunk_index: int
    score: float


class RagAnswerResponse(BaseModel):
    """Extractive RAG answer response."""

    request_id: str
    answer_type: str
    answer: str
    citations: list[Citation]
    model_version: str
    elapsed_ms: float
