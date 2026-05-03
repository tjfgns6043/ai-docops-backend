from services.api.app.db.models import (
    ApiKey,
    Document,
    DocumentChunk,
    IdempotencyKey,
    InferenceRequest,
    Job,
    Tenant,
    Vector,
)


def test_initial_schema_tables_are_declared() -> None:
    table_names = {
        Tenant.__tablename__,
        ApiKey.__tablename__,
        Document.__tablename__,
        DocumentChunk.__tablename__,
        Job.__tablename__,
        InferenceRequest.__tablename__,
        IdempotencyKey.__tablename__,
    }

    assert table_names == {
        "tenants",
        "api_keys",
        "documents",
        "document_chunks",
        "jobs",
        "inference_requests",
        "idempotency_keys",
    }


def test_chunk_embedding_uses_pgvector_384() -> None:
    embedding_type = DocumentChunk.__table__.c.embedding.type

    assert embedding_type.get_col_spec() == "vector(384)"


def test_vector_bind_processor_formats_pgvector_literal() -> None:
    processor = Vector(3).bind_processor(None)

    assert processor([1, 2.5, -0.25]) == "[1.0,2.5,-0.25]"


def test_metadata_columns_keep_database_name() -> None:
    assert Document.metadata_.property.columns[0].name == "metadata"
    assert DocumentChunk.metadata_.property.columns[0].name == "metadata"
