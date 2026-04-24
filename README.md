[![CI](https://github.com/JoMag-Inc/firebuster/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/JoMag-Inc/firebuster/actions/workflows/ci.yml)
[![Docker Publish](https://github.com/JoMag-Inc/firebuster/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/JoMag-Inc/firebuster/actions/workflows/docker-publish.yml)
[![GitHub release](https://img.shields.io/github/v/release/JoMag-Inc/firebuster)](https://github.com/JoMag-Inc/firebuster/releases)
[![Python](https://img.shields.io/badge/python-3.13+-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Docker Image](https://img.shields.io/badge/ghcr.io-firebuster-0db7ed?logo=docker&logoColor=white)](https://ghcr.io/jomag-inc/firebuster)

# Firebuster Peer Review Setup

## Overall architecture

For the architecture we went for a three layer arcitectures with handling of requests happen in `restapi.py` through fastapi handlers. We only implemented one handler for
Time to flashover `/api/v1/ttf`. This takes latitude and longitude paramaters for fetching weather data and calculating ttf. For business logic we use a service layer.
This includes services for retrieving weather data from MET. A MQTT service for publishing to broker, and a TTFSevice that has the sole responsibility of returning TTF data based on longitude and latitude.
For this it has a toolset consisting of the other services and a database. The database is accessed through the third layer. The Reposirory layer. This abstracts saving, getting and deleting entries from the database.

For authentication we have set up a key cloak instance on the service. To get wether data one first have to retrieve a token for api access. Currently it only has access for a couple minutes at the time for testing.

The system is orchastraded using docker compose, both for local development and on the server. This make deploying simple, but has limitations related to scalability of course.

![architecture](./assets/architecture.png)

## Prerequisites

- Docker
- Docker Compose
- `curl`
- `jq`

### Extra notes for Windows

#### some dependencies must be installed explicitly

- Open PowerShell as admin
- Install Chocolatey [(Install guide)](https://chocolatey.org/install)
- Install `make` and `jq`

```
winget install jqlang.jq
```

```
choco install make
```

#### other notes

- Docker desktop must be launched separately before docker commands can be used in PowerShell.

## Setup

The stack runs four services:

- Firebuster API
- Keycloak
- PostgreSQL
- Mosquitto (MQTT broker)

Clone the repository:

```bash
git clone https://github.com/JoMag-Inc/firebuster.git
cd firebuster
```

Create `.env` from the example:

```bash
cp .env.example .env
```

Start the stack:

```bash
# Foreground
docker compose up --build

# Background
docker compose up --build -d
```

Stop the stack:

```bash
# Keep database data
docker compose down

# Remove containers and volumes (destructive)
docker compose down -v
```

## Keycloak Import Note (Important)

The realm import file is `kcdb/data/import/realm-export.json`.

Keycloak imports this file on startup when the Keycloak database is empty. If you already have data in your local volumes, old users/realm data can remain.

If you need to force a clean re-import (for example, to include the latest `tester` user), run:

```bash
docker compose down -v
docker compose up --build -d
```

## Test the API

Before testing the API we need to add the tables to the new database.
This is done through a migration script with `alembic`.

# !IMPORTANT RUN MIGRATION

To do the up migration to the latest version of the database run:

```bash
make migrate
```

this is a command we have added in Makefile, which also contains a lot of other handy commands to check the application

Test user in the current realm export:

| Username | Password   | Roles |
| -------- | ---------- | ----- |
| tester   | secrettest | ADMIN |

Get an access token:

```bash
#MacOS/Linux
token=$(curl -s -X POST "http://localhost:8080/realms/Firebuster/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=firebuster-api&username=tester&password=secrettest&grant_type=password" \
  | jq -r '.access_token')
```

```powershell
#Windows
$token = (curl.exe -s -X POST "http://localhost:8080/realms/Firebuster/protocol/openid-connect/token" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "client_id=firebuster-api&username=tester&password=secrettest&grant_type=password" `
  | ConvertFrom-Json).access_token
```

```powershell
#verify token (Windows)
Write-Host "Token: $token"
```

Quick checks:

```bash
# Public health endpoint (no auth)
curl http://localhost:8000/api/health

# Protected TTF endpoint (requires ADMIN role)
curl -s "http://localhost:8000/api/v1/ttf/?longitude=50&latitude=50" \
  -H "Authorization: Bearer $token" | jq
```

```powershell
#Windows
curl.exe http://localhost:8000/api/health

curl.exe -s "http://localhost:8000/api/v1/ttf/?longitude=50&latitude=50" `
  -H "Authorization: Bearer $token" | jq
```

## OpenAPI Docs

With the stack running, open:

```text
http://localhost:8000/docs
```

Use the token from above in the Authorize dialog, then run the protected endpoints from the UI.
It can be viewed in the terminal by typing `$token`

## MQTT

Firebuster can publish fire risk updates to MQTT whenever `GET /api/v1/ttf/` is called.

By default (from `.env.example`) it publishes to:

- Broker host: `mosquitto`
- Broker port: `1883`
- Topic: `firebuster/fire-risk`

The payload is JSON and contains:

- `event` (`fire_risk_update`)
- `source` (`fresh` when calculated now, `cache` when served from DB)
- `latitude`, `longitude`, `calculated_at`
- `ttf_points`

You can test a subscriber locally with:

```bash
#MacOS/Linux
docker run --rm -it --network host eclipse-mosquitto:2 \
  mosquitto_sub -h 127.0.0.1 -p 1883 -t firebuster/fire-risk -v
```

```powershell
#Windows
docker run --rm -it --network host eclipse-mosquitto:2 `
  mosquitto_sub -h 127.0.0.1 -p 1883 -t firebuster/fire-risk -v
```

Then call the API endpoint and you should see a published message on the topic.
Here are the commands again in just in case:

```bash
#MacOS/Linux
token=$(curl -s -X POST "http://localhost:8080/realms/Firebuster/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=firebuster-api&username=tester&password=secrettest&grant_type=password" \
  | jq -r '.access_token')
```

```powershell
#Windows
$token = (curl.exe -s -X POST "http://localhost:8080/realms/Firebuster/protocol/openid-connect/token" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "client_id=firebuster-api&username=tester&password=secrettest&grant_type=password" `
  | ConvertFrom-Json).access_token
```

```powershell
#verify token (Windows)
Write-Host "Token: $token"
```

```bash
# Protected TTF endpoint (requires ADMIN role)
curl -s "http://localhost:8000/api/v1/ttf/?longitude=50&latitude=50" \
  -H "Authorization: Bearer $token" | jq
```

```powershell
#Windows
curl.exe http://localhost:8000/api/health

curl.exe -s "http://localhost:8000/api/v1/ttf/?longitude=50&latitude=50" `
  -H "Authorization: Bearer $token" | jq
```

## Test with Client

We have also made a client [firebuster-explorer](https://github.com/JoMag-Inc/firebuster-explorer)
Clone and try it if you want to!

make inspect-kc-db
```
