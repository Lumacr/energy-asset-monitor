
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas


def create_telemetry(
    db: Session,
    asset_id: int,
    telemetry: schemas.TelemetryCreate,
) -> models.Telemetry:
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

    try:
        # Create the telemetry record
        db_telemetry = models.Telemetry(
            asset_id=asset_id,
            state=telemetry.state,
            energy_kwh=telemetry.energy_kwh,
            timestamp=telemetry.timestamp or datetime.now(timezone.utc),
        )

        db.add(db_telemetry)
        db.commit()
        db.refresh(db_telemetry)

        return db_telemetry

    except Exception:
        db.rollback()
        raise
