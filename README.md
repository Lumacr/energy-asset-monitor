# Energy Asset Monitor API

A lightweight, containerized REST API designed to manage and monitor Energy Storage Systems (BESS).

This project simulates the core backend infrastructure needed to register Energy Storage Systems (BESS), ingest real-time charging/discharging telemetry, and perform time-series data aggregation.

## Tech Stack
- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL (with SQLAlchemy ORM)
- **Data Validation:** Pydantic
- **Infrastructure:** Docker & Docker Compose

## How to Run (Local Environment)

The entire application is containerized. You do not need to install Python or PostgreSQL on your local machine to run it.

1. Clone the repository:
   ```bash
   git clone https://github.com/Lumacr/energy-asset-monitor.git
   cd energy-asset-monitor
   ```

2. Spin up the Database and the API:
   ```bash
   docker compose up --build -d
   ```

3. Open the interactive API documentation (Swagger UI):
   http://localhost:8000/docs

Note: The API automatically handles database and table creation on startup.

## API Endpoints

- **POST /assets/** - Register a new energy storage asset with its capacity (kWh).

  - **POST /assets/{asset_id}/telemetry/** - Ingest real-time telemetry (`charging/discharging/idle`) and the energy transacted.

- **GET /assets/{asset_id}/summary/** - Returns the aggregated total energy charged and discharged over the last 24 hours. The calculation is optimized using native SQL aggregation (`func.sum`) rather than in-memory Python loops.

## Future Improvements (Production Readiness)

While this is a minimal viable product, scaling this for a real-world algorithmic trading platform would require several architectural upgrades:

- **Database Migration:** Move from vanilla `PostgreSQL` to `TimescaleDB` to heavily optimize the ingestion and querying of time-series telemetry data.

- **Asynchronous Processing:** Implement `Celery` & `Redis` to handle incoming data streams asynchronously, ensuring the API remains highly responsive during traffic spikes.

- **Testing:** Implement a comprehensive test suite using `pytest` for unit and integration testing.

- **Security & Auth:** Add JWT-based authentication and rate-limiting to protect the endpoints.

- **Alembic:** Introduce `Alembic` for proper database schema migration management.
