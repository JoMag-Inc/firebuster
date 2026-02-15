.PHONY: dev prod

dev:
	uv run fastapi dev app/main.py

prod:
	uv run fastapi run app/main.py
