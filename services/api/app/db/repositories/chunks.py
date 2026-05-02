"""Document chunk repository."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DocumentChunk


def select_chunks_for_document(
    tenant_id: UUID,
    document_id: UUID,
) -> Select[tuple[DocumentChunk]]:
    """Build a tenant-scoped chunk lookup statement."""
    return (
        select(DocumentChunk)
        .where(DocumentChunk.tenant_id == tenant_id, DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )


class ChunkRepository:
    """Persistence methods for document chunks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_document(self, tenant_id: UUID, document_id: UUID) -> list[DocumentChunk]:
        """List chunks for one tenant-owned document."""
        result = await self.session.execute(select_chunks_for_document(tenant_id, document_id))
        return list(result.scalars())
