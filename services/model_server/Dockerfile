FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
RUN pip install --no-cache-dir ".[model]"

COPY services /app/services

CMD ["uvicorn", "services.model_server.app.main:app", "--host", "0.0.0.0", "--port", "9000"]
