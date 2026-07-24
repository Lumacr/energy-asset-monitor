from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    capacity_kwh = Column(Float, nullable=False)

    # Defines the relationship with telemetry records
    telemetry_records = relationship("Telemetry", back_populates="asset")


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    # We use timezone-aware datetimes for energy data
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # State should ideally be "charging", "discharging", or "idle"
    state = Column(String, nullable=False)
    energy_kwh = Column(Float, nullable=False)

    # Links back to the parent asset
    asset = relationship("Asset", back_populates="telemetry_records")