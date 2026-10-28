
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# --- Asset Schemas ---
class AssetBase(BaseModel):
    name: str
    capacity_kwh: float = Field(gt=0, allow_inf_nan=False)


class AssetCreate(AssetBase):
    pass


class AssetResponse(AssetBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Telemetry Schemas ---
class TelemetryBase(BaseModel):
    state: Literal["charging", "discharging", "idle"]
    energy_kwh: float = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_idle_energy(self):
        if self.state == "idle" and self.energy_kwh != 0:
            raise ValueError("Energy must be zero when state is idle.")
        return self


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
