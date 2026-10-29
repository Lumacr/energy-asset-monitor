
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


def get_asset_summary(
    db: Session,
    asset_id: int,
) -> schemas.AssetSummaryResponse:
    # Validate that the asset exists
    db_asset = (
        db.query(models.Asset)
        .filter(models.Asset.id == asset_id)
        .first()
    )

    if not db_asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    # Calculate the time window (last 24 hours)
    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(hours=24)

    # Sum charged energy
    charged = (
        db.query(func.sum(models.Telemetry.energy_kwh))
        .filter(
            models.Telemetry.asset_id == asset_id,
            models.Telemetry.state == "charging",
            models.Telemetry.timestamp >= twenty_four_hours_ago,
            models.Telemetry.timestamp <= now,
        )
        .scalar()
        or 0.0
    )

    # Sum discharged energy
    discharged = (
        db.query(func.sum(models.Telemetry.energy_kwh))
        .filter(
            models.Telemetry.asset_id == asset_id,
            models.Telemetry.state == "discharging",
            models.Telemetry.timestamp >= twenty_four_hours_ago,
            models.Telemetry.timestamp <= now,
        )
        .scalar()
        or 0.0
    )

    return schemas.AssetSummaryResponse(
        asset_id=asset_id,
        total_charged_kwh=charged,
        total_discharged_kwh=discharged,
    )
