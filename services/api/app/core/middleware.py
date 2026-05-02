"""API middleware."""

from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_ID_HEADER = "X-Request-ID"


def create_request_id() -> str:
    """Create a public request ID."""
    return f"req_{uuid4().hex}"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a request ID to each request and response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or create_request_id()
        request.state.request_id = request_id

        started_at = perf_counter()
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers["X-Response-Time-Ms"] = f"{(perf_counter() - started_at) * 1000:.3f}"
        return response
