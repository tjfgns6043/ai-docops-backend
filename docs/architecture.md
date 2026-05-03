# Architecture

AI DocOps separates runtime responsibilities into small services:

- `api`: FastAPI public API, auth, tenant guard, cache/rate-limit orchestration.
- `model-server`: FastAPI internal inference API for embeddings, extractive summary, and prototype classification.
- `worker`: Celery worker for document indexing and long summary jobs.
- `postgres`: PostgreSQL 16 with pgvector for documents, chunks, jobs, API keys, and inference audit rows.
- `redis`: cache, rate-limit counters, and Celery broker/backend.
- `prometheus`, `grafana`, `jaeger`: local observability profile.

The API does not load ML models. Workers and API call the model server over HTTP so model memory, model failures, and model scaling stay behind one serving boundary.

All resource lookups use `tenant_id`. Cross-tenant document, chunk, and job access is intentionally returned as `404 RESOURCE_NOT_FOUND`.
