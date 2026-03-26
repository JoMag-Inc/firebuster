.PHONY: dev prod

dev:
	uv run fastapi dev app/restapi.py

prod:
	uv run python -m app.main

test:
	uv run python -m unittest discover -s tests
