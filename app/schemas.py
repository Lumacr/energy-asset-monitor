from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# --- Asset Schemas ---
class AssetBase(BaseModel):
    name: str
    capacity_kwh: float

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Telemetry Schemas ---
class TelemetryBase(BaseModel):
    state: str
    energy_kwh: float

class TelemetryCreate(TelemetryBase):
    timestamp: Optional[datetime] = None

class TelemetryResponse(TelemetryBase):
    id: int
    asset_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Summary Schema ---
class AssetSummaryResponse(BaseModel):
    asset_id: int
    total_charged_kwh: float
    total_discharged_kwh: float