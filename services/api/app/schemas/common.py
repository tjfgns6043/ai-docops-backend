"""Common API schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness response."""

    status: str = Field(examples=["ok"])
    service: str = Field(examples=["api"])


class ReadyResponse(BaseModel):
    """Readiness response."""

    status: str = Field(examples=["ready"])
    service: str = Field(examples=["api"])
    checks: dict[str, str] = Field(default_factory=dict)


class ErrorDetail(BaseModel):
    """Error detail payload."""

    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    """Public error envelope."""

    error: ErrorDetail
