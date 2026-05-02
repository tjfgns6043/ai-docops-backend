from uuid import UUID

from sqlalchemy.dialects import postgresql

from services.api.app.db.repositories.chunks import select_chunks_for_document
from services.api.app.db.repositories.documents import select_document_by_id
from services.api.app.db.repositories.idempotency import select_idempotency_key
from services.api.app.db.repositories.inference_requests import select_inference_requests_for_tenant
from services.api.app.db.repositories.jobs import select_job_by_id, select_job_by_idempotency_key

TENANT_ID = UUID("00000000-0000-0000-0000-00000000000a")
RESOURCE_ID = UUID("00000000-0000-0000-0000-000000000001")


def compile_sql(statement: object) -> str:
    compiled = statement.compile(dialect=postgresql.dialect())
    return str(compiled)


def test_document_lookup_requires_tenant_id() -> None:
    sql = compile_sql(select_document_by_id(TENANT_ID, RESOURCE_ID))

    assert "documents.tenant_id" in sql
    assert "documents.id" in sql


def test_job_lookup_requires_tenant_id() -> None:
    sql = compile_sql(select_job_by_id(TENANT_ID, RESOURCE_ID))

    assert "jobs.tenant_id" in sql
    assert "jobs.id" in sql


def test_job_idempotency_lookup_requires_tenant_id() -> None:
    sql = compile_sql(select_job_by_idempotency_key(TENANT_ID, "idem-key"))

    assert "jobs.tenant_id" in sql
    assert "jobs.idempotency_key" in sql


def test_chunk_lookup_requires_tenant_id() -> None:
    sql = compile_sql(select_chunks_for_document(TENANT_ID, RESOURCE_ID))

    assert "document_chunks.tenant_id" in sql
    assert "document_chunks.document_id" in sql


def test_inference_lookup_requires_tenant_id() -> None:
    sql = compile_sql(select_inference_requests_for_tenant(TENANT_ID))

    assert "inference_requests.tenant_id" in sql


def test_idempotency_lookup_requires_tenant_id() -> None:
    sql = compile_sql(select_idempotency_key(TENANT_ID, "idem-key"))

    assert "idempotency_keys.tenant_id" in sql
    assert "idempotency_keys.key" in sql
