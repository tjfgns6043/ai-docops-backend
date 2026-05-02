# ADR-0003: Use Celery And Redis

## Status

Accepted

## Decision

Use Celery with Redis broker for async document indexing and long summary jobs.

## Consequences

- Long work stays out of the HTTP request path.
- Retry and job status behavior can be demonstrated.
- Redis availability becomes part of readiness.
