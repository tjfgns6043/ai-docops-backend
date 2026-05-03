"""Document service."""

from http import HTTPStatus
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.hashing import sha256_hex
from libs.common.status import DOCUMENT_UPLOADED, JOB_QUEUED

from ..core.errors import ApiError
from ..core.security import Principal
from ..db.models import Document, Job
from ..db.repositories.documents import DocumentRepository
from ..db.repositories.jobs import JobRepository
from ..schemas.documents import DocumentCreateRequest


def job_response(job: Job) -> dict[str, object]:
    """Return a common job creation response dictionary."""
    return {
        "job_id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "result_url": f"/v1/jobs/{job.id}",
    }


class DocumentService:
    """Document workflow methods."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.documents = DocumentRepository(session)
        self.jobs = JobRepository(session)

    async def create_document(
        self,
        principal: Principal,
        payload: DocumentCreateRequest,
    ) -> Document:
        """Persist an uploaded document."""
        document = Document(
            tenant_id=principal.tenant_id,
            owner_id=principal.owner_id,
            title=payload.title,
            language=payload.language,
            source_hash=sha256_hex(payload.text),
            text=payload.text,
            status=DOCUMENT_UPLOADED,
            metadata_=payload.metadata,
        )
        try:
            created = await self.documents.add(document)
            await self.session.commit()
        except Exception as exc:
            await self.session.rollback()
            raise ApiError(
                "DATABASE_UNAVAILABLE",
                "database is temporarily unavailable",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        return created

    async def get_document(self, principal: Principal, document_id: UUID) -> Document:
        """Return a tenant-owned document."""
        try:
            document = await self.documents.get_by_id(principal.tenant_id, document_id)
        except Exception as exc:
            raise ApiError(
                "DATABASE_UNAVAILABLE",
                "database is temporarily unavailable",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        if document is None:
            raise ApiError("RESOURCE_NOT_FOUND", "document not found", HTTPStatus.NOT_FOUND)
        return document

    async def create_index_job(
        self,
        principal: Principal,
        document_id: UUID,
        idempotency_key: str | None,
    ) -> Job:
        """Create an indexing job and enqueue worker processing."""
        await self.get_document(principal, document_id)
        request_hash = sha256_hex(f"index:{principal.tenant_id}:{document_id}")
        try:
            if idempotency_key:
                existing = await self.jobs.get_by_idempotency_key(
                    principal.tenant_id,
                    idempotency_key,
                )
                if existing:
                    return existing
            job = Job(
                tenant_id=principal.tenant_id,
                owner_id=principal.owner_id,
                job_type="index_document",
                status=JOB_QUEUED,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                payload={"document_id": str(document_id)},
            )
            created = await self.jobs.add(job)
            await self.session.commit()
            enqueue_index_document(created.id)
        except ApiError:
            raise
        except Exception as exc:
            await self.session.rollback()
            raise ApiError(
                "DATABASE_UNAVAILABLE",
                "database is temporarily unavailable",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        return created


def enqueue_index_document(job_id: UUID) -> None:
    """Enqueue an index task if Celery is available."""
    try:
        from services.worker.app.tasks.index_document import index_document_task

        index_document_task.delay(str(job_id))
    except Exception:
        return
