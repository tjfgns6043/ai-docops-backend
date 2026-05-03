FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
RUN pip install --no-cache-dir .

COPY services /app/services
COPY libs /app/libs
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini
COPY scripts /app/scripts

CMD ["uvicorn", "services.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
