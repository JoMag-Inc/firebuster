# firebuster

Firebuster is a REST API service that can calculate the TTF (time to flashover) for a given location.
It is currently under construction.

## Install requirements

This project uses the [UV package](https://docs.astral.sh/uv/) and project manager.

If you do not already have it:

Install macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

```

Windows:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Package managers:

```bash
pipx install uv

brew install uv

# see installation docs for more
```

When you have uv installed run:

```bash
# Install dependencies from pyproject.toml
uv sync
```

To add a new package run

```bash
uv add <package-name>
```

To update all dependencies:

```bash
uv lock --upgrade
```

## Running code

To run the scripts do:

```bash
uv run python scriptname.py
```

## Tests

The tests are located in `tests/`. To run the tests one can use the `run_tests.sh` like this:

```bash
./run_tests.sh
```

It contains a command for locating all tests in the tests/ directory and runs them

## FAST API

Firebuster uses FastAPI for creating its endpoints. Here are some run instructions to get the server up and going

The entry of the application is placed in `app/main.py` and can be run with the following commands

```bash

# To run in dev mode with auto-reload
uv run fastapi dev app/main.py

# While run mode is used for prod environments
uv run fastapi run app/main.py
```

To spare your fingers we have set up a Makefile for running them with:

```bash
make dev

make prod
```

While the server is running it can be tested using your favorite tools. Here is a curl command to get started:

```bash
curl http://127.0.0.1:8000/api/health
```

You can also use the built in `/docs` route in FastAPI:

```bash
http://127.0.0.1:8000/docs
```
