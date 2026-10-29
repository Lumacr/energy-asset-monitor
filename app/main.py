from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, database
from .services import asset_service, telemetry_service, summary_service


# Initialize FastAPI application
app = FastAPI(
    title="Energy Asset Monitor API",
    description="API for managing and monitoring energy storage systems (BESS).",
    version="1.0.0"
)


# 1. Register a new Asset (Battery)
@app.post("/assets/", response_model=schemas.AssetResponse, status_code=201)
def create_asset(
    asset: schemas.AssetCreate,
    db: Session = Depends(database.get_db),
):
    return asset_service.create_asset(db, asset)




# 2. Record telemetry (Charging/Discharging)
@app.post(
    "/assets/{asset_id}/telemetry/",
    response_model=schemas.TelemetryResponse,
    status_code=201,
)
def create_telemetry(
    asset_id: int,
    telemetry: schemas.TelemetryCreate,
    db: Session = Depends(database.get_db),
):
    return telemetry_service.create_telemetry(
        db,
        asset_id,
        telemetry,
    )



# 3. 24-hour summary (Analytics endpoint)
@app.get(
    "/assets/{asset_id}/summary/",
    response_model=schemas.AssetSummaryResponse,
)
def get_asset_summary(
    asset_id: int,
    db: Session = Depends(database.get_db),
):
    return summary_service.get_asset_summary(db, asset_id)
