"""Document API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DocumentCreateRequest(BaseModel):
    """Document upload request."""

    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=100_000)
    language: str = Field(pattern="^(ko|en|mixed)$")
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, metadata: dict[str, object]) -> dict[str, object]:
        """Limit metadata key count."""
        if len(metadata) > 20:
            raise ValueError("metadata can contain at most 20 keys")
        return metadata


class DocumentResponse(BaseModel):
    """Uploaded document response."""

    document_id: UUID
    tenant_id: UUID
    version: int
    status: str
    text_length: int
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    """Document detail response."""

    title: str
    language: str
    metadata: dict[str, object]


class IndexJobCreateResponse(BaseModel):
    """Index job creation response."""

    job_id: UUID
    job_type: str
    status: str
    result_url: str
