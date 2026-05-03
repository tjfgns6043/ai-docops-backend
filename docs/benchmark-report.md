# Benchmark Report

Measured on 2026-05-03 with the core Docker Compose stack running locally. Requests were executed from inside the API container against `127.0.0.1:8000`, so these numbers are useful as a repeatable smoke benchmark rather than an external load test.

| Endpoint | Scenario | p50 | p95 | p99 | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| `/health` | 50 sequential requests | 0.47ms | 0.77ms | 11.40ms | In-container smoke benchmark |
| `/v1/summaries` | 10 sequential requests, warmed cache | 11.90ms | 21.77ms | 27.48ms | `docker compose exec api python scripts/benchmark_summary.py` |
| `/v1/search` | 10 sequential requests, seeded chunks | 11.64ms | 12.69ms | 151.18ms | `docker compose exec api python scripts/benchmark_search.py` |

These are not production capacity claims. A real load test should run from outside the Compose network with controlled concurrency, clean database state, and a fixed model cache state.
