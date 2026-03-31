# Declare command targets (not real files).
.PHONY: dev prod test lint format-check ci-check migrate migrate-down migrate-status inspect-db inspect-kc-db

# Start API in development mode with auto-reload.
dev:
	uv run fastapi dev app/restapi.py

# Start API in production-like mode.
prod:
	uv run python -m app.main

# Run all unit tests in tests/.
test:
	uv run python -m unittest discover -s tests

# Run fast lint checks used in CI.
lint:
	uvx ruff check . --select E9,F63,F7,F82

# Verify code formatting without changing files.
format-check:
	uvx ruff format --check .

# Convenience target for local CI-style checks.
ci-check: lint test

# Apply all pending migrations
migrate:
	docker compose exec app uv run alembic upgrade head

# Roll back the last migration.
migrate-down:
	docker compose exec app uv run alembic downgrade -1

# Show current migration state.
migrate-status:
	docker compose exec app uv run alembic current

# Inspect tables in the firebuster app database.
inspect-db:
	docker compose exec postgres psql -U postgres -d firebuster -c "\dt"

# Inspect tables in the keycloak database.
inspect-kc-db:
	docker compose exec postgres psql -U postgres -d keycloak -c "\dt"

