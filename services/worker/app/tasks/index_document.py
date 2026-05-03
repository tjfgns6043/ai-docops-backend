"""Document indexing task."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select

from libs.common.status import (
    DOCUMENT_INDEXED,
    DOCUMENT_INDEXING,
    JOB_COMPLETED,
    JOB_FAILED,
    JOB_RUNNING,
)
from services.api.app.db.models import Document, DocumentChunk, Job
from services.model_server.app.services.text_processing import chunk_text, estimate_tokens

from ..celery_app import celery_app
from ..clients.model_client import WorkerModelClient
from ..core.config import get_settings
from ..db.session import make_session_factory


@celery_app.task(name="index_document")
def index_document_task(job_id: str) -> None:
    """Celery task wrapper for document indexing."""
    asyncio.run(index_document(UUID(job_id)))


async def index_document(job_id: UUID) -> None:
    """Index a document into chunks and embeddings."""
    settings = get_settings()
    session_factory = make_session_factory()
    async with session_factory() as session:
        job = await session.get(Job, job_id)
        if job is None:
            return
        job.status = JOB_RUNNING
        job.started_at = datetime.now(UTC)
        await session.commit()

        try:
            document_id = UUID(str(job.payload["document_id"]))
            document = (
                await session.execute(
                    select(Document).where(
                        Document.id == document_id,
                        Document.tenant_id == job.tenant_id,
                    )
                )
            ).scalar_one()
            document.status = DOCUMENT_INDEXING
            texts = chunk_text(document.text)
            embeddings = await WorkerModelClient(settings).embed(texts)
            chunks = [
                DocumentChunk(
                    tenant_id=document.tenant_id,
                    document_id=document.id,
                    document_version=document.version,
                    chunk_index=index,
                    text=chunk,
                    token_estimate=estimate_tokens(chunk),
                    embedding=embedding,
                    embedding_model_version=settings.model_version,
                    preprocess_version=settings.preprocess_version,
                    metadata_={"title": document.title},
                )
                for index, (chunk, embedding) in enumerate(zip(texts, embeddings, strict=True))
            ]
            session.add_all(chunks)
            document.status = DOCUMENT_INDEXED
            job.status = JOB_COMPLETED
            job.result = {"chunks_created": len(chunks)}
            job.completed_at = datetime.now(UTC)
            await session.commit()
        except Exception as exc:
            await session.rollback()
            job = await session.get(Job, job_id)
            if job is not None:
                job.status = JOB_FAILED
                job.error_code = "JOB_FAILED"
                job.error_message = str(exc)
                job.completed_at = datetime.now(UTC)
                await session.commit()
