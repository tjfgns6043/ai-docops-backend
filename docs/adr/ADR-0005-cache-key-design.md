# ADR-0005: Cache Key Design

## Status

Accepted

## Decision

Cache keys include tenant ID, operation, model version, preprocess version, and input hash.

## Consequences

- Tenant cache contamination is avoided.
- Model and preprocessing changes do not reuse stale results.
