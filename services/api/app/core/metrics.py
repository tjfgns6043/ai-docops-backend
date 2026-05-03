"""API metrics."""

from fastapi.responses import Response

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
except ModuleNotFoundError:  # pragma: no cover
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    Counter = Histogram = None  # type: ignore[assignment]
    generate_latest = None  # type: ignore[assignment]

if Counter is not None:
    HTTP_REQUESTS = Counter(
        "http_requests_total",
        "API HTTP requests",
        ["method", "path", "status"],
    )
    HTTP_DURATION = Histogram(
        "http_request_duration_seconds",
        "API HTTP request duration",
        ["method", "path"],
    )
    API_ERRORS = Counter("api_errors_total", "API errors", ["code"])
else:
    HTTP_REQUESTS = HTTP_DURATION = API_ERRORS = None


def observe_http_request(method: str, path: str, status_code: int, elapsed_seconds: float) -> None:
    """Record HTTP request metrics."""
    if HTTP_REQUESTS is None:
        return
    normalized_path = path if not path.startswith("/v1/") else path.split("?")[0]
    HTTP_REQUESTS.labels(method, normalized_path, str(status_code)).inc()
    HTTP_DURATION.labels(method, normalized_path).observe(elapsed_seconds)


def observe_api_error(code: str) -> None:
    """Record an API error."""
    if API_ERRORS is not None:
        API_ERRORS.labels(code).inc()


async def metrics() -> Response:
    """Return Prometheus metrics."""
    if generate_latest is None:
        body = (
            "# HELP ai_docops_build_info Build information placeholder\n"
            "# TYPE ai_docops_build_info gauge\n"
            'ai_docops_build_info{service="api"} 1\n'
        )
        return Response(content=body, media_type=CONTENT_TYPE_LATEST)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
