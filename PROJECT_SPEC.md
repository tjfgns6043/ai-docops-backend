# AI DocOps Backend Project Spec

You are implementing an AI backend portfolio project named `ai-docops-backend`.

## Goal

Build an operational AI document processing backend that runs on Mac M1 Pro 32GB using Docker Compose.

## Core Services

1. FastAPI API server
2. FastAPI model server
3. Celery worker
4. PostgreSQL 16 with pgvector
5. Redis
6. Prometheus, Grafana, Jaeger observability profile
7. Kubernetes manifests for local kind demo

## Important Constraints

- Do not run a local generative LLM as a core dependency.
- Do not use Triton or KServe in the implementation.
- Use CPU-only model inference.
- Load the ML model only in model-server, not in API server or worker.
- Use `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- Embedding dimension is 384.
- Summary must be extractive, not generative.
- Classification must be prototype embedding based, not fine-tuned.
- RAG answer must be extractive and return citations.
- Every resource query must be tenant-isolated.
- Never log raw document text or API keys.

## Functional Requirements

- API key authentication with hashed keys.
- Tenant isolation.
- Document upload.
- Async document indexing job.
- Sync short text summary.
- Async long document summary job.
- Text classification.
- Semantic search.
- Extractive RAG answer.
- Redis cache.
- Redis-based rate limit.
- Idempotency key for job creation.
- Timeout and 503 mapping for model-server failures.
- PostgreSQL persistence.
- Prometheus metrics.
- OpenTelemetry traces.
- JSON structured logs.
- Failure scenario scripts.
- Benchmark scripts.
- README, ADRs, runbooks, benchmark report.

## Implementation Phases

1. Scaffold
2. API health/config/logging
3. DB models/migrations
4. Auth and tenant guard
5. Model server
6. Sync summary and prediction
7. Document upload and indexing jobs
8. Search and extractive RAG answer
9. Observability
10. Failure scenarios and benchmark
11. Kubernetes manifests
12. Documentation polish

## Quality Requirements

- Use type hints.
- Use Pydantic schemas.
- Use SQLAlchemy async.
- Use Alembic migrations.
- Use pytest.
- Use ruff.
- Add unit and integration tests.
- Add OpenAPI contract test.
- Keep code modular: routers, services, repositories, model_client.
- Add clear error response structure.
