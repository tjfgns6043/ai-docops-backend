"""Model server metrics."""

from time import perf_counter
from typing import Any

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
except ModuleNotFoundError:  # pragma: no cover
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    Counter = Gauge = Histogram = None  # type: ignore[assignment]
    generate_latest = None  # type: ignore[assignment]

from fastapi.responses import Response

if Counter is not None:
    MODEL_REQUESTS = Counter(
        "model_requests_total",
        "Model server requests",
        ["operation", "status", "model_version"],
    )
    MODEL_DURATION = Histogram(
        "model_request_duration_seconds",
        "Model request duration",
        ["operation", "model_version"],
    )
    MODEL_BATCH_SIZE = Histogram(
        "model_batch_size",
        "Model request batch size",
        ["operation"],
    )
    MODEL_LOADED = Gauge("model_loaded", "Model loaded", ["model_version"])
else:
    MODEL_REQUESTS = MODEL_DURATION = MODEL_BATCH_SIZE = MODEL_LOADED = None


class model_timer:
    """Context manager that records model request metrics."""

    def __init__(self, operation: str, model_version: str, batch_size: int = 1) -> None:
        self.operation = operation
        self.model_version = model_version
        self.batch_size = batch_size
        self.started_at = 0.0
        self.elapsed_ms = 0.0

    def __enter__(self) -> "model_timer":
        self.started_at = perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        elapsed = perf_counter() - self.started_at
        self.elapsed_ms = elapsed * 1000
        status = "error" if exc_type else "ok"
        if MODEL_REQUESTS is not None:
            MODEL_REQUESTS.labels(self.operation, status, self.model_version).inc()
            MODEL_DURATION.labels(self.operation, self.model_version).observe(elapsed)
            MODEL_BATCH_SIZE.labels(self.operation).observe(self.batch_size)


def mark_model_loaded(model_version: str, loaded: bool) -> None:
    """Record whether the model is loaded."""
    if MODEL_LOADED is not None:
        MODEL_LOADED.labels(model_version).set(1 if loaded else 0)


async def metrics() -> Response:
    """Return Prometheus metrics."""
    if generate_latest is None:
        body = (
            "# HELP model_loaded Model loaded\n"
            "# TYPE model_loaded gauge\n"
            'model_loaded{model_version="fallback"} 1\n'
        )
        return Response(content=body, media_type=CONTENT_TYPE_LATEST)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
