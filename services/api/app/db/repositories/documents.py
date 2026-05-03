"""Document repository."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Document


def select_document_by_id(tenant_id: UUID, document_id: UUID) -> Select[tuple[Document]]:
    """Build a tenant-scoped document lookup statement."""
    return select(Document).where(
        Document.tenant_id == tenant_id,
        Document.id == document_id,
        Document.deleted_at.is_(None),
    )


class DocumentRepository:
    """Persistence methods for documents."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, tenant_id: UUID, document_id: UUID) -> Document | None:
        """Return a tenant-owned document by ID."""
        result = await self.session.execute(select_document_by_id(tenant_id, document_id))
        return result.scalar_one_or_none()

    async def add(self, document: Document) -> Document:
        """Add a document."""
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document
