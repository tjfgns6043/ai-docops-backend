FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
    && pip install --no-cache-dir \
        "fastapi>=0.111" \
        "prometheus-client>=0.20" \
        "pydantic>=2.7" \
        "pydantic-settings>=2.3" \
        "sentence-transformers>=3.0" \
        "uvicorn[standard]>=0.30" \
    && python -c "import importlib.metadata as md; forbidden=[dist.metadata['Name'] for dist in md.distributions() if dist.metadata['Name'].startswith(('nvidia-', 'triton'))]; assert not forbidden, forbidden"

COPY services /app/services

CMD ["uvicorn", "services.model_server.app.main:app", "--host", "0.0.0.0", "--port", "9000"]
