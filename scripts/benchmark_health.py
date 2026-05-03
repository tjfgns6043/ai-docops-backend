"""Simple health endpoint benchmark."""

import asyncio
import statistics
from time import perf_counter

import httpx

API_URL = "http://localhost:8000"


async def run_once(client: httpx.AsyncClient) -> float:
    """Run one health request and return elapsed milliseconds."""
    started_at = perf_counter()
    response = await client.get("/health")
    response.raise_for_status()
    return (perf_counter() - started_at) * 1000


async def benchmark(iterations: int = 50) -> None:
    """Run the benchmark."""
    async with httpx.AsyncClient(base_url=API_URL, timeout=5.0) as client:
        values = [await run_once(client) for _ in range(iterations)]
    print("health benchmark")
    print(f"p50_ms={statistics.median(values):.2f}")
    print(f"p95_ms={sorted(values)[int(len(values) * 0.95) - 1]:.2f}")
    print(f"p99_ms={max(values):.2f}")


def main() -> None:
    """Run health benchmark."""
    asyncio.run(benchmark())


if __name__ == "__main__":
    main()
