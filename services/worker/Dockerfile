FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml /app/
COPY services/worker /app/services/worker
COPY libs /app/libs

CMD ["python", "-m", "services.worker.app.celery_app"]
