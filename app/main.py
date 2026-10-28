from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from . import models, schemas, database


# Initialize FastAPI application
app = FastAPI(
    title="Energy Asset Monitor API",
    description="API for managing and monitoring energy storage systems (BESS).",
    version="1.0.0"
)


# 1. Register a new Asset (Battery)
@app.post("/assets/", response_model=schemas.AssetResponse, status_code=201)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(database.get_db)):
    db_asset = models.Asset(name=asset.name, capacity_kwh=asset.capacity_kwh)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


# 2. Record telemetry (Charging/Discharging)
@app.post("/assets/{asset_id}/telemetry/", response_model=schemas.TelemetryResponse, status_code=201)
def create_telemetry(asset_id: int, telemetry: schemas.TelemetryCreate, db: Session = Depends(database.get_db)):
    # Validate if the asset exists
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Record the telemetry
    db_telemetry = models.Telemetry(
        asset_id=asset_id,
        state=telemetry.state,
        energy_kwh=telemetry.energy_kwh,
        timestamp=telemetry.timestamp or datetime.now(timezone.utc)
    )
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry


# 3. 24-hour summary (Analytics endpoint)
@app.get("/assets/{asset_id}/summary/", response_model=schemas.AssetSummaryResponse)
def get_asset_summary(asset_id: int, db: Session = Depends(database.get_db)):
    # Validate if the asset exists
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Calculate the time window (last 24 hours)
    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(hours=24)

    # Sum charged energy using native SQLAlchemy (more efficient than Python memory loops)
    charged = db.query(func.sum(models.Telemetry.energy_kwh)).filter(
        models.Telemetry.asset_id == asset_id,
        models.Telemetry.state == "charging",
        models.Telemetry.timestamp >= twenty_four_hours_ago,
        models.Telemetry.timestamp <= now,
    ).scalar() or 0.0

    # Sum discharged energy
    discharged = db.query(func.sum(models.Telemetry.energy_kwh)).filter(
        models.Telemetry.asset_id == asset_id,
        models.Telemetry.state == "discharging",
        models.Telemetry.timestamp >= twenty_four_hours_ago
    ).scalar() or 0.0

    return schemas.AssetSummaryResponse(
        asset_id=asset_id,
        total_charged_kwh=charged,
        total_discharged_kwh=discharged
    )