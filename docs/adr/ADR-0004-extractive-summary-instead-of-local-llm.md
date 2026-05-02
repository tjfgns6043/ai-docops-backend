# ADR-0004: Use Extractive Summary Instead Of Local LLM

## Status

Accepted

## Decision

Do not run a local generative LLM as a core dependency. Use extractive summarization and extractive RAG answers.

## Consequences

- Local Docker Compose runs more reliably on the target machine.
- The project emphasizes AI backend operations over model quality claims.
- README must clearly state this limitation.
