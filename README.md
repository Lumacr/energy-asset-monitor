# Energy Asset Monitor API

A containerized REST API for managing and monitoring Battery Energy Storage Systems (BESS).

The project simulates a backend service that registers energy assets, records charging and discharging telemetry, and calculates energy consumption and production summaries over a rolling 24-hour window.

## Features

- Register energy assets with their name and storage capacity.
- Record telemetry events with a state, energy value, and optional timestamp.
- Validate telemetry states and energy values, including the requirement that idle events have zero energy.
- Calculate total charged and discharged energy over the last 24 hours using SQL aggregation.
- Manage database schema changes with Alembic migrations.
- Run automated tests with pytest.
- Validate tests and database migrations through GitHub Actions.

## Tech Stack

- **Language:** Python 3.11 in the application container.
- **API Framework:** FastAPI.
- **Data Validation:** Pydantic.
- **Database:** PostgreSQL 15.
- **ORM:** SQLAlchemy.
- **Database Migrations:** Alembic.
- **Containerization:** Docker and Docker Compose.
- **Testing:** pytest and FastAPI TestClient.
- **Continuous Integration:** GitHub Actions.

## Prerequisites

To run the application using Docker Compose, you need:

- Git.
- Docker with Docker Compose support.

To run tests or database migrations directly on your machine, you also need Python and the dependencies listed in `requirements.txt`.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Lumacr/energy-asset-monitor.git
cd energy-asset-monitor
```

### 2. Start PostgreSQL

Start the database service:

```bash
docker compose up -d db
```

Wait until PostgreSQL is ready before continuing.

### 3. Apply database migrations

Install the Python dependencies in your local environment, then apply the migrations:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
alembic upgrade head
```

The commands above assume a Unix-like shell and that PostgreSQL is available at the default local connection configured by the project.

### 4. Start the application

Build and start the API container:

```bash
docker compose up --build -d api
```

The API is available at:

- **Interactive API documentation (Swagger UI):** http://localhost:8000/docs
- **Alternative API documentation (ReDoc):** http://localhost:8000/redoc

To stop the services:

```bash
docker compose down
```

The PostgreSQL data is stored in a Docker volume and is retained when the containers are stopped. To remove the database volume as well, use `docker compose down -v`. This permanently deletes the data stored in that volume.

## API Endpoints

### Register an asset

`POST /assets/`

Request body:

```json
{
  "name": "Battery Alpha",
  "capacity_kwh": 500.0
}
```

The capacity must be greater than zero.

### Record telemetry

`POST /assets/{asset_id}/telemetry/`

Request body:

```json
{
  "state": "charging",
  "energy_kwh": 25.5,
  "timestamp": "2026-10-28T10:00:00Z"
}
```

The `timestamp` field is optional. If omitted, the API assigns the current UTC time.

Supported states are:

- `charging`
- `discharging`
- `idle`

Energy values must be non-negative. When the state is `idle`, the energy value must be zero. The referenced asset must exist.

### Retrieve an energy summary

`GET /assets/{asset_id}/summary/`

Returns the total energy charged and discharged for the specified asset over the previous 24 hours.

Example response:

```json
{
  "asset_id": 1,
  "total_charged_kwh": 25.5,
  "total_discharged_kwh": 10.0
}
```

The values above are illustrative. The endpoint uses SQL aggregation to calculate the totals and returns zero when there are no matching telemetry records. The referenced asset must exist.

## Database Migrations

Alembic manages the database schema.

Apply all migrations:

```bash
alembic upgrade head
```

Check whether the SQLAlchemy models match the current database schema:

```bash
alembic check
```

These commands require a reachable PostgreSQL database and a correctly configured `DATABASE_URL`, unless the default local connection settings are appropriate.

## Running Tests

Activate your virtual environment and install the project dependencies. Then run:

```bash
python -m pytest -v
```

The current API test suite uses an in-memory SQLite database, keeping the tests isolated from the local PostgreSQL instance.

## Continuous Integration

GitHub Actions runs two independent jobs on pushes and pull requests targeting `main`:

- **`test`:** runs the automated test suite.
- **`migration-check`:** starts PostgreSQL 15, applies the Alembic migrations to a fresh database, and runs `alembic check`.

This verifies the API tests and database migration workflow separately.

## Project Structure

```text
energy-asset-monitor/
├── app/
│   ├── main.py       # API endpoints and application setup
│   ├── models.py     # SQLAlchemy database models
│   ├── schemas.py    # Pydantic request and response schemas
│   └── database.py   # Database engine and session management
├── alembic/
│   ├── versions/     # Versioned database migrations
│   └── env.py        # Alembic configuration
├── tests/            # Automated tests
├── .github/
│   └── workflows/
│       └── ci.yml    # GitHub Actions workflow
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## Future Improvements

Potential improvements include:

- Add integration tests that execute the API against PostgreSQL.
- Introduce authentication and authorization.
- Add rate limiting and more robust production security controls.
- Improve observability with structured logging, metrics, and health checks.
- Evaluate time-series database extensions such as TimescaleDB if ingestion volume and query patterns justify them.
- Introduce asynchronous processing if telemetry ingestion requirements demand it.
