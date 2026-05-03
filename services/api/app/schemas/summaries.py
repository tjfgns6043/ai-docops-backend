"""Summary API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class SummaryRequest(BaseModel):
    """Synchronous short-text summary request."""

    text: str = Field(min_length=1, max_length=8_000)
    max_sentences: int = Field(default=3, ge=1, le=10)
    language: str = Field(default="mixed", pattern="^(ko|en|mixed)$")
    model_version: str = "multilingual-minilm-l12-v1"


class SummaryResponse(BaseModel):
    """Synchronous summary response."""

    request_id: str
    summary: str
    model_version: str
    preprocess_version: str
    cached: bool
    elapsed_ms: float


class SummaryJobCreateRequest(BaseModel):
    """Async summary job request."""

    document_id: UUID | None = None
    text: str | None = Field(default=None, min_length=1, max_length=100_000)
    max_sentences: int = Field(default=5, ge=1, le=10)
    model_version: str = "multilingual-minilm-l12-v1"

    @model_validator(mode="after")
    def validate_source(self) -> "SummaryJobCreateRequest":
        """Require exactly one source."""
        if bool(self.document_id) == bool(self.text):
            raise ValueError("send exactly one of document_id or text")
        return self
