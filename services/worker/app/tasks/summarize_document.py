"""Document summary task."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID

from libs.common.status import JOB_COMPLETED, JOB_FAILED, JOB_RUNNING
from services.api.app.db.models import Document, Job

from ..celery_app import celery_app
from ..clients.model_client import WorkerModelClient
from ..core.config import get_settings
from ..db.session import make_session_factory


@celery_app.task(name="summarize_document")
def summarize_document_task(job_id: str) -> None:
    """Celery task wrapper for summary jobs."""
    asyncio.run(summarize_document(UUID(job_id)))


async def summarize_document(job_id: UUID) -> None:
    """Run an async extractive summary job."""
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
            payload = dict(job.payload)
            if "document_id" in payload:
                document = await session.get(Document, UUID(str(payload["document_id"])))
                if document is None or document.tenant_id != job.tenant_id:
                    raise ValueError("document not found")
                text = document.text
            else:
                text = str(payload["text"])
            response = await WorkerModelClient(settings).summarize(
                text,
                int(payload.get("max_sentences", 5)),
            )
            job.status = JOB_COMPLETED
            job.result = {
                "summary": response["summary"],
                "model_version": response["model_version"],
                "cached": False,
            }
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
