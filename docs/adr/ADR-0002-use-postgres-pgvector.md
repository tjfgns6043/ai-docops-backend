# ADR-0002: Use PostgreSQL And pgvector

## Status

Accepted

## Decision

Use PostgreSQL with pgvector instead of a separate vector database for the local portfolio scope.

## Consequences

- Documents, chunks, jobs, and embeddings stay in one datastore.
- Local operation remains simpler.
- This choice should be revisited for larger vector workloads.
