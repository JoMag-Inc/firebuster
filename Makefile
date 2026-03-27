# Declare command targets (not real files).
.PHONY: dev prod test lint format-check ci-check

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
