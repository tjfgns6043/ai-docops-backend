FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml /app/
COPY services/api /app/services/api
COPY libs /app/libs

CMD ["python", "-m", "services.api.app.main"]
