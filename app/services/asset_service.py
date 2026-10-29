
from sqlalchemy.orm import Session

from app import models, schemas


def create_asset(db: Session, asset: schemas.AssetCreate) -> models.Asset:
    try:
        db_asset = models.Asset(
            name=asset.name,
            capacity_kwh=asset.capacity_kwh,
        )

        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)

        return db_asset

    except Exception:
        db.rollback()
        raise
