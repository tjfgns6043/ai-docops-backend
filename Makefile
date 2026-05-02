.PHONY: up down test lint migrate seed benchmark

up:
	docker compose up --build

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

benchmark:
	python scripts/benchmark_summary.py
	python scripts/benchmark_search.py
