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
make up
make migrate
make seed
make smoke
```

The development API key seeded by `make seed` is:

```text
ak_dev_tenant_a_123456
```

## 6. API Examples

Core endpoints:

- `POST /v1/documents`
- `POST /v1/documents/{document_id}/index-jobs`
- `POST /v1/summaries`
- `POST /v1/summary-jobs`
- `POST /v1/predictions`
- `POST /v1/search`
- `POST /v1/rag/answers`
- `GET /v1/jobs/{job_id}`

Run the automated end-to-end smoke flow against a running Compose stack:

```bash
make smoke
```

The smoke test verifies readiness, summary caching, prototype classification, document upload, async indexing, semantic search, and extractive RAG citations.

## 7. Async Job Flow

Document indexing and long summary requests create a DB-backed `jobs` row, enqueue Celery work, update job status, and expose results through `/v1/jobs/{job_id}` and `/v1/summary-jobs/{job_id}`.

## 8. Model Server Design

The model server owns model loading and inference. API and worker services call it over HTTP. Docker installs the PyTorch CPU wheel before `sentence-transformers` and fails the image build if `nvidia-*` or `triton` packages are present. If `sentence-transformers` cannot be loaded in a local test environment, deterministic fallback embeddings keep unit tests runnable; production Docker runs with fallback disabled.

## 9. Cache And Idempotency

Cache keys must include `tenant_id`, operation, model version, preprocess version, and input hash. Job creation endpoints will support `Idempotency-Key`.

## 10. Tenant Isolation And Security

All `/v1/*` APIs will require `X-API-Key`. API keys are stored as hashes. Resource queries must include tenant filters and return 404 for cross-tenant access.

## 11. Observability

Observability includes JSON logs, Prometheus-compatible `/metrics` endpoints, Prometheus scrape config, alert rules, a Grafana dashboard skeleton, and a Jaeger service in the observability profile.

## 12. Failure Scenarios

Failure scripts live under `scripts/` and cover model server down, Redis down, and DB down. Expected behavior is documented in `docs/failure-scenarios.md`.

## 13. Benchmark Results

Benchmark scripts live under `scripts/benchmark_health.py`, `scripts/benchmark_summary.py`, and `scripts/benchmark_search.py`. Current smoke benchmark results are recorded in `docs/benchmark-report.md`.

## 14. Kubernetes Deployment

Local Kubernetes manifests live under `infra/k8s`.

```bash
kind create cluster --name ai-docops
docker build -f services/api/Dockerfile -t ai-docops-api:local .
docker build -f services/model_server/Dockerfile -t ai-docops-model-server:local .
docker build -f services/worker/Dockerfile -t ai-docops-worker:local .
kind load docker-image ai-docops-api:local --name ai-docops
kind load docker-image ai-docops-model-server:local --name ai-docops
kind load docker-image ai-docops-worker:local --name ai-docops
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/
kubectl wait --for=condition=ready pod --all -n ai-docops --timeout=300s
kubectl exec -n ai-docops deployment/api -- alembic upgrade head
kubectl exec -n ai-docops deployment/api -- python scripts/seed_dev_data.py
kubectl port-forward -n ai-docops service/api 8000:8000
```

Verified locally with kind on 2026-05-03: API, model-server, worker, PostgreSQL, and Redis pods reached `Ready`; API `/ready` reported database, Redis, and model-server as `ok`.

This local HPA example is for Kubernetes manifest demonstration only. Real AI model scaling should consider model latency, queue depth, GPU utilization, and cost metrics, not CPU alone.

## 15. ADRs

Architecture decisions live in `docs/adr`.

## 16. Limitations

- No local generative LLM is used as a core dependency.
- Summary and RAG answers are extractive.
- Classification is prototype embedding based.
- Local Kubernetes manifests are for portfolio demonstration, not production hardening.

## 17. Future Work

- Add concurrent load tests with a larger document corpus.
- Add deeper dashboard panels.
- Add production-grade secret management.
- Evaluate dedicated vector databases for larger datasets.
