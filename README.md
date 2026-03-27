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

The tests are located in `tests/`. To run the tests one can use the `make test` command like this:

```bash
make test
```

It contains a command for locating all tests in the tests/ directory and runs them

In some tests we use `Mock` and `patch` to fake external API calls.
This makes tests faster, more stable, and independent of internet/API uptime.

## MET integration scope

Current MET scope in this branch:

- Fetch weather data from MET using explicit coordinates (`lat`, `lon`).
- Transform MET payload to CSV with columns needed by the TTF calculator:
	`timestamp`, `temperature`, `humidity`, `wind_speed`.

Not included in this branch:

- Converting user location text (for example "Førde in Norway") to coordinates.
- UI input forms and frontend integration.
- End-to-end API endpoint that chains location -> MET -> TTF.

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

## Docker

The app can be built into a Docker image and started from Compose. The stack runs three services: the Firebuster API, Keycloak, and a PostgreSQL database.

**First time setup:**

```bash
# Copy and fill in the environment file
cp .env.example .env
```

Edit `.env` with your values — see `.env.example` for the required fields.

**Start the stack:**

```bash
# Build and start in the foreground
docker compose up --build

# Or start in the background
docker compose up --build -d
```

**Stop the stack:**

```bash
# Stop containers — database data is preserved
docker compose down

# Stop containers AND delete the database volume (destructive — all data lost)
docker compose down -v
```

> **Warning:** `docker compose down -v` permanently deletes the PostgreSQL volume. Only use this if you want to reset the database to a clean state (e.g. during development). Never run this on a production server unless you intend to wipe all Keycloak data.

**Services and ports:**

| Service | URL |
|---|---|
| Firebuster API | `http://localhost:8000` |
| Keycloak | `http://localhost:8080` |
| PostgreSQL | `localhost:5432` |

## CD: Publish Docker image to GHCR

This repository now includes a release workflow in `.github/workflows/docker-publish.yml`.

What it does:

- Builds the Docker image from `Dockerfile`.
- Pushes image to GitHub Container Registry (GHCR):
  `ghcr.io/<owner>/<repo>`
- Runs automatically when you push a version tag like `v0.1.0`.

Create and push a release tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

After the workflow finishes, pull the image with:

```bash
docker pull ghcr.io/<owner>/<repo>:v0.1.0
```

## Usage

All protected endpoints require a Bearer token from Keycloak. Obtain one first:

```bash
token=$(curl -s -X POST "http://localhost:8080/realms/Firebuster/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=firebuster-api&username=<user>&password=<password>&grant_type=password" \
  | jq -r '.access_token')
```

**Health check (no auth required):**

```bash
curl http://localhost:8000/api/health
```

**TTF calculation:**

```bash
curl -s "http://localhost:8000/api/v1/ttf/?longitude=10&latitude=60" \
  -H "Authorization: Bearer $token" | jq
```

Returns a list of TTF (time to flashover) values in hours paired with the weather data used for each calculation.

**Protected endpoints:**

| Endpoint | Required role |
|---|---|
| `GET /api/v1/protected` | `USER` |
| `GET /api/v1/protected/service` | `APP_USER` |
| `GET /api/v1/admin` | `ADMIN` |
| `GET /api/v1/admin/service` | `APP_ADMIN` |
| `GET /api/v1/ttf/` | `USER` |

The interactive API docs are available at `http://localhost:8000/docs` while the server is running.

## Keycloak

Authentication to the REST API is managed using Keycloak. It runs in a Docker container backed by a PostgreSQL database for persistent storage. The Firebuster realm and client are imported automatically on first boot from `kcdb/data/import/realm-export.json`.
