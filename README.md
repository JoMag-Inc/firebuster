# firebuster

Firebuster is a REST API service that can claculate the ttf(time to flashover) given a certain location.
It is currently under construction

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

## FAST API coming soon
