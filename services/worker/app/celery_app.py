"""Celery app."""

from .core.config import get_settings
from .core.logging import configure_logging

settings = get_settings()
configure_logging(settings)

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover
    Celery = None  # type: ignore[assignment]


class LocalTask:
    """Fallback task object used when Celery is not installed."""

    def __init__(self, fn):
        self.fn = fn

    def delay(self, *args, **kwargs):
        """Run synchronously in fallback mode."""
        return self.fn(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


class LocalCelery:
    """Tiny fallback with the Celery task decorator API."""

    def task(self, *args, **kwargs):
        def decorator(fn):
            return LocalTask(fn)

        return decorator


if Celery is None:
    celery_app = LocalCelery()
else:
    celery_app = Celery(
        "ai_docops_worker",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=[
            "services.worker.app.tasks.index_document",
            "services.worker.app.tasks.summarize_document",
        ],
    )
    celery_app.conf.update(task_track_started=True, worker_prefetch_multiplier=1)


if __name__ == "__main__":
    print("Start the worker with: celery -A services.worker.app.celery_app.celery_app worker")
