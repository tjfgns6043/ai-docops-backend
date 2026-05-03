.PHONY: up up-obs down test lint migrate seed smoke benchmark openapi

up:
	docker compose up --build

up-obs:
	docker compose --profile obs up --build

down:
	docker compose down

test:
	python -m pytest

lint:
	ruff check .

migrate:
	alembic upgrade head

seed:
	python scripts/seed_dev_data.py

smoke:
	python scripts/smoke_compose.py

benchmark:
	python scripts/benchmark_summary.py
	python scripts/benchmark_search.py

openapi:
	python scripts/export_openapi.py
