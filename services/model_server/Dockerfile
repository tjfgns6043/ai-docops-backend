FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml /app/
COPY services/model_server /app/services/model_server

CMD ["python", "-m", "services.model_server.app.main"]
