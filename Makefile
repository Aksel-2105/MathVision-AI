.PHONY: install dev backend frontend test test-backend test-frontend lint format typecheck migrate build docker-up docker-down

install:
	python -m pip install -e backend[dev]
	pnpm --dir frontend install

dev:
	@echo "Run 'make backend' and 'make frontend' in separate terminals."

backend:
	python -m uvicorn app.main:app --app-dir backend --reload

frontend:
	pnpm --dir frontend dev

test: test-backend test-frontend

test-backend:
	python -m pytest backend/tests

test-frontend:
	pnpm --dir frontend test -- --run

lint:
	python -m ruff check backend
	pnpm --dir frontend lint

format:
	python -m ruff format backend

typecheck:
	python -m mypy backend/app
	pnpm --dir frontend typecheck

migrate:
	python -m alembic -c backend/alembic.ini upgrade head

build:
	pnpm --dir frontend build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
