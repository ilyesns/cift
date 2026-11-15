.PHONY: up down logs test test-unit test-api test-int lint fmt migrate revision downgrade psql web-dev web-lint web-build superadminw

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	docker compose exec api pytest -q

test-unit:
	docker compose exec api pytest -q tests/unit

test-api:
	docker compose exec api pytest -q tests/api

test-int:
	docker compose exec api pytest -q -m integration

lint:
	docker compose exec api ruff check .
	docker compose exec api ruff format --check .

fmt:
	docker compose exec api ruff check --fix .
	docker compose exec api ruff format .

migrate:
	docker compose exec api alembic upgrade head

revision:
	docker compose exec api alembic revision --autogenerate -m "$(m)"

downgrade:
	docker compose exec api alembic downgrade -1

psql:
	docker compose exec db psql -U cift -d cift

web-dev:
	cd web && npm run dev

web-lint:
	cd web && npm run lint && npm run typecheck


web-build:
	cd web && npm run build


superadmin:
	docker compose exec api python -m app.cli create-superadmin $(email) "$(name)"