"""Unified API error responses."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .metrics import observe_api_error


class ApiError(Exception):
    """Application error rendered with the public error envelope."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code


def get_request_id(request: Request) -> str:
    """Read the request ID placed by middleware."""
    return str(getattr(request.state, "request_id", "req_unknown"))


def error_response(status_code: int, code: str, message: str, request_id: str) -> JSONResponse:
    """Build a consistent error envelope."""
    observe_api_error(code)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
            },
        },
    )


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    """Render application errors."""
    return error_response(exc.status_code, exc.code, exc.message, get_request_id(request))


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Render framework HTTP errors with the public envelope."""
    try:
        phrase = HTTPStatus(exc.status_code).phrase
    except ValueError:
        phrase = "Error"

    code = phrase.upper().replace(" ", "_")
    return error_response(
        exc.status_code,
        code,
        str(exc.detail),
        get_request_id(request),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Render validation errors without leaking request bodies."""
    return error_response(
        HTTPStatus.UNPROCESSABLE_ENTITY,
        "VALIDATION_ERROR",
        "request validation failed",
        get_request_id(request),
    )


def add_exception_handlers(app: FastAPI) -> None:
    """Register public exception handlers."""
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
