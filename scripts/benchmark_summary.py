"""Simple summary benchmark."""

import asyncio
import statistics
from time import perf_counter

import httpx

API_URL = "http://localhost:8000"
API_KEY = "ak_dev_tenant_a_123456"


async def run_once(client: httpx.AsyncClient) -> float:
    """Run one summary request and return elapsed milliseconds."""
    started_at = perf_counter()
    response = await client.post(
        "/v1/summaries",
        headers={"X-API-Key": API_KEY},
        json={
            "text": "FastAPI serves the API. The model server handles embeddings. "
            "Redis provides cache and rate limiting. PostgreSQL stores documents.",
            "max_sentences": 2,
            "language": "en",
        },
    )
    response.raise_for_status()
    return (perf_counter() - started_at) * 1000


async def benchmark(iterations: int = 10) -> None:
    """Run the benchmark."""
    async with httpx.AsyncClient(base_url=API_URL, timeout=10.0) as client:
        values = [await run_once(client) for _ in range(iterations)]
    print("summary benchmark")
    print(f"p50_ms={statistics.median(values):.2f}")
    print(f"p95_ms={sorted(values)[int(len(values) * 0.95) - 1]:.2f}")
    print(f"p99_ms={max(values):.2f}")


def main() -> None:
    """Run summary benchmark."""
    asyncio.run(benchmark())


if __name__ == "__main__":
    main()
