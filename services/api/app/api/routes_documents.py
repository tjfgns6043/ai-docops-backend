"""Document routes."""

from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import Principal, require_scope
from ..db.session import get_session
from ..schemas.documents import (
    DocumentCreateRequest,
    DocumentDetailResponse,
    DocumentResponse,
    IndexJobCreateResponse,
)
from ..services.document_service import DocumentService, job_response

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=HTTPStatus.CREATED,
)
async def create_document(
    payload: DocumentCreateRequest,
    principal: Principal = Depends(require_scope("documents:write")),
    session: AsyncSession = Depends(get_session),
) -> DocumentResponse:
    """Upload a document."""
    document = await DocumentService(session).create_document(principal, payload)
    return DocumentResponse(
        document_id=document.id,
        tenant_id=document.tenant_id,
        version=document.version,
        status=document.status,
        text_length=len(document.text),
        created_at=document.created_at,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: UUID,
    principal: Principal = Depends(require_scope("documents:read")),
    session: AsyncSession = Depends(get_session),
) -> DocumentDetailResponse:
    """Get a tenant-owned document."""
    document = await DocumentService(session).get_document(principal, document_id)
    return DocumentDetailResponse(
        document_id=document.id,
        tenant_id=document.tenant_id,
        version=document.version,
        status=document.status,
        text_length=len(document.text),
        created_at=document.created_at,
        title=document.title,
        language=document.language,
        metadata=document.metadata_,
    )


@router.post(
    "/{document_id}/index-jobs",
    response_model=IndexJobCreateResponse,
    status_code=HTTPStatus.ACCEPTED,
)
async def create_index_job(
    document_id: UUID,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    principal: Principal = Depends(require_scope("documents:write")),
    session: AsyncSession = Depends(get_session),
) -> IndexJobCreateResponse:
    """Create an async document indexing job."""
    job = await DocumentService(session).create_index_job(principal, document_id, idempotency_key)
    return IndexJobCreateResponse(**job_response(job))
