"""Model server logging."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from .config import Settings


class JsonFormatter(logging.Formatter):
    """Minimal JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": "model-server",
            "event": getattr(record, "event", record.getMessage()),
            "message": record.getMessage(),
        }
        return json.dumps(payload, separators=(",", ":"))


def configure_logging(settings: Settings) -> None:
    """Configure JSON logging."""
    logger = logging.getLogger()
    logger.setLevel(settings.log_level.upper())
    if any(isinstance(handler.formatter, JsonFormatter) for handler in logger.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
