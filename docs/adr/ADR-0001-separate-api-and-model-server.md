# ADR-0001: Separate API And Model Server

## Status

Accepted

## Decision

FastAPI API server does not load the ML model directly. A separate model server loads the embedding model and exposes internal inference endpoints.

## Consequences

- API workers avoid duplicate model loading.
- Model failures can be mapped and isolated.
- Model serving can scale independently.
