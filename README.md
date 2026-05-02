# AI DocOps Backend

FastAPI 기반 AI 문서 요약, 분류, 검색 백엔드 포트폴리오입니다.

This project focuses on AI backend and MLOps engineering, not on building a state-of-the-art summarization model.
The summarization endpoint uses extractive summarization based on sentence embeddings.
The classification endpoint uses prototype label embeddings, not a fine-tuned classifier.
The RAG answer endpoint is extractive and returns citations without calling a generative LLM.

## 1. What This Project Is

`ai-docops-backend` is an operational AI document processing backend. It is designed to demonstrate model serving boundaries, async jobs, caching, tenant isolation, observability, and local deployment practices.

## 2. Why This Project Matters For AI Backend / MLOps

The project emphasizes production-oriented AI backend engineering: a separate model server, database-backed jobs, Redis-based cache and rate limits, structured logs, metrics, traces, failure scenarios, and Kubernetes manifests.

## 3. Architecture

The intended runtime shape is:

- API server: accepts authenticated tenant-scoped requests.
- Model server: loads the CPU embedding model once and exposes internal inference endpoints.
- Worker: processes long-running indexing and summary jobs.
- PostgreSQL + pgvector: stores documents, jobs, chunks, inference records, and embeddings.
- Redis: handles cache, rate limits, and Celery broker responsibilities.

## 4. Tech Stack

- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x async
- Alembic
- PostgreSQL 16 + pgvector
- Redis 7
- Celery
- httpx
- Prometheus
- OpenTelemetry + Jaeger
- Docker Compose
- Kubernetes manifests for local kind demos

## 5. Local Setup

```bash
cp .env.example .env
make test
make lint
```

Runtime services will be filled in across later phases.

## 6. API Examples

Planned core endpoints:

- `POST /v1/documents`
- `POST /v1/documents/{document_id}/index-jobs`
- `POST /v1/summaries`
- `POST /v1/summary-jobs`
- `POST /v1/predictions`
- `POST /v1/search`
- `POST /v1/rag/answers`
- `GET /v1/jobs/{job_id}`

## 7. Async Job Flow

Document indexing and long summary requests are intended to create a DB-backed job, enqueue Celery work, update job status, and expose job results through read endpoints.

## 8. Model Server Design

The model server owns model loading and inference. API and worker services call it over HTTP.

## 9. Cache And Idempotency

Cache keys must include `tenant_id`, operation, model version, preprocess version, and input hash. Job creation endpoints will support `Idempotency-Key`.

## 10. Tenant Isolation And Security

All `/v1/*` APIs will require `X-API-Key`. API keys are stored as hashes. Resource queries must include tenant filters and return 404 for cross-tenant access.

## 11. Observability

Planned observability includes JSON logs, Prometheus metrics, OpenTelemetry traces, Grafana dashboards, and Jaeger trace inspection.

## 12. Failure Scenarios

Failure scenarios will cover model server down, Redis down, DB down, and queue backlog.

## 13. Benchmark Results

Benchmark results will be recorded after implementation. Placeholder targets are documented in `docs/benchmark-report.md`.

## 14. Kubernetes Deployment

Local Kubernetes manifests will live under `infra/k8s`.

## 15. ADRs

Architecture decisions live in `docs/adr`.

## 16. Limitations

- No local generative LLM is used as a core dependency.
- Summary and RAG answers are extractive.
- Classification is prototype embedding based.
- Local Kubernetes manifests are for portfolio demonstration, not production hardening.

## 17. Future Work

- Add measured benchmark results.
- Add deeper dashboard panels.
- Add production-grade secret management.
- Evaluate dedicated vector databases for larger datasets.
