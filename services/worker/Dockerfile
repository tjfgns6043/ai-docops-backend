FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
RUN pip install --no-cache-dir .

COPY services /app/services
COPY libs /app/libs

CMD ["celery", "-A", "services.worker.app.celery_app.celery_app", "worker", "--loglevel=INFO", "--concurrency=1"]
