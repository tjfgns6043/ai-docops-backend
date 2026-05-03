# Benchmark Report

Measured on 2026-05-03 with the core Docker Compose stack running locally. Requests were executed from the host against `localhost:8000`, so these numbers are useful as a repeatable smoke benchmark rather than an external load test.

| Endpoint | Scenario | p50 | p95 | p99 | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| `/health` | 50 sequential requests | 2.13ms | 5.74ms | 14.77ms | `python scripts/benchmark_health.py` |
| `/v1/summaries` | 10 sequential requests, warmed cache | 13.18ms | 13.96ms | 22.82ms | `python scripts/benchmark_summary.py` |
| `/v1/search` | 10 sequential requests, seeded chunks | 12.85ms | 14.19ms | 19.61ms | `python scripts/benchmark_search.py` |

These are not production capacity claims. A real load test should run from outside the Compose network with controlled concurrency, clean database state, and a fixed model cache state.
