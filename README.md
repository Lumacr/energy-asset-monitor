# Energy Asset Monitor API

A containerized REST API for managing and monitoring Battery Energy Storage Systems (BESS).

The project simulates a backend service that registers energy assets, records charging and discharging telemetry, and calculates energy summaries over a rolling 24-hour window.

## Features

- Register energy assets with their name and storage capacity.
- Record telemetry events with a state, energy value, and optional timestamp.
- Validate telemetry states and energy values, including the requirement that idle events have zero energy.
- Calculate total charged and discharged energy over the last 24 hours using SQL aggregation.
- Manage database schema changes with Alembic migrations.
- Run automated unit, API, and service-layer tests.
- Run integration tests against PostgreSQL.
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

To run database migrations or tests directly on your machine, you also need Python and the dependencies listed in `requirements.txt`.

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

The default local database connection is:

```text
postgresql+psycopg2://user:password@localhost:5432/energy_db
```

The application supports overriding this connection through the `DATABASE_URL` environment variable.

### 3. Install dependencies and apply migrations

Create and activate a virtual environment, then install the project dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Apply the database migrations:

```bash
alembic upgrade head
```

These commands assume that PostgreSQL is reachable through the default local connection or the configured `DATABASE_URL`.

### 4. Start the API

Ensure that PostgreSQL is healthy and accepting connections before starting the API container.

Build and start the API container:

```bash
docker compose up --build -d api
```

The API container connects to PostgreSQL using the Docker Compose service name `db`.

The API is available at:

- **Interactive API documentation (Swagger UI):** http://localhost:8000/docs
- **Alternative API documentation (ReDoc):** http://localhost:8000/redoc

To stop the services:

```bash
docker compose down
```

PostgreSQL data is stored in a Docker volume and is retained when the containers are stopped. To remove the database volume as well, run:

```bash
docker compose down -v
```

**Warning:** This permanently deletes the data stored in the PostgreSQL volume.

## Architecture

The application separates HTTP request handling, business logic, data validation, and database persistence.

- **`app/main.py`:** Defines the FastAPI application and HTTP endpoints. Endpoints delegate operations to the service layer.
- **`app/services/`:** Contains the asset, telemetry, and summary services. The write services manage database transactions, including commits, refreshes, and rollbacks.
- **`app/schemas.py`:** Defines Pydantic schemas for request validation and response serialization.
- **`app/models.py`:** Defines the SQLAlchemy database models and their relationships.
- **`app/database.py`:** Configures the database engine, session factory, and database dependency.
- **`alembic/`:** Contains the database migration environment and versioned migrations.
- **`tests/`:** Contains API and service-layer tests, including integration tests against PostgreSQL.

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

Returns the created asset with HTTP status `201 Created`.

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

Returns the created telemetry record with HTTP status `201 Created`.

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

The values above are illustrative. The endpoint uses SQL aggregation to calculate the totals, excludes telemetry outside the rolling 24-hour window (including future timestamps), and returns zero when there are no matching records. The referenced asset must exist.

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

By default, the test configuration uses an in-memory SQLite database. This allows the tests to run without connecting to the local PostgreSQL instance.

To run the suite against PostgreSQL, set `TEST_DATABASE_URL` to a dedicated test database:

```bash
export TEST_DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/energy_test_db"
python -m pytest -v
```

Ensure that the PostgreSQL test database exists and is reachable before running the tests. The test setup creates the schema from the SQLAlchemy models and removes it during teardown, so use a dedicated test database rather than a database containing application data.

## Continuous Integration

GitHub Actions runs three jobs on pushes and pull requests targeting `main`:

- **`test`:** runs the automated test suite using the default SQLite test configuration.
- **`migration-check`:** starts PostgreSQL 15, applies the Alembic migrations to a fresh database, and runs `alembic check` to verify schema consistency.
- **`integration-test`:** starts PostgreSQL 15 and runs the automated test suite against a dedicated PostgreSQL test database.

Together, these jobs validate application behavior, database migrations, and integration with PostgreSQL.

## Project Structure

```text
energy-asset-monitor/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── services/
│       ├── asset_service.py
│       ├── telemetry_service.py
│       └── summary_service.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_asset_service.py
│   ├── test_telemetry_service.py
│   └── test_summary_service.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## Future Improvements

Potential improvements include:

- Introduce authentication and authorization.
- Add rate limiting and more robust production security controls.
- Improve observability with structured logging, metrics, and health checks.
- Evaluate time-series database extensions such as TimescaleDB if ingestion volume and query patterns justify them.
- Introduce asynchronous processing if telemetry ingestion requirements demand it.
