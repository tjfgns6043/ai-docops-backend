"""Worker logging."""

import json
import logging
from datetime import UTC, datetime

from .config import Settings


class JsonFormatter(logging.Formatter):
    """Minimal JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "service": "worker",
                "event": getattr(record, "event", record.getMessage()),
                "message": record.getMessage(),
            },
            separators=(",", ":"),
        )


def configure_logging(settings: Settings) -> None:
    """Configure worker JSON logging."""
    logger = logging.getLogger()
    logger.setLevel(settings.log_level.upper())
    if any(isinstance(handler.formatter, JsonFormatter) for handler in logger.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
