"""Structured JSON logging for the API service."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from .config import Settings


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter for stdout logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", "api"),
            "event": getattr(record, "event", record.getMessage()),
            "message": record.getMessage(),
        }

        for field in ("request_id", "tenant_id", "method", "path", "status_code", "elapsed_ms"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        return json.dumps(payload, separators=(",", ":"))


def configure_logging(settings: Settings) -> None:
    """Configure process logging once for JSON stdout output."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())

    if any(isinstance(handler.formatter, JsonFormatter) for handler in root_logger.handlers):
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger.handlers = [handler]
