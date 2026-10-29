
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.services import telemetry_service


def test_create_telemetry_commits_and_returns_telemetry():
    db = Mock(spec=Session)

    db_asset = models.Asset(
        id=1,
        name="Battery A",
        capacity_kwh=100.0,
    )
    db.query.return_value.filter.return_value.first.return_value = db_asset

    telemetry = schemas.TelemetryCreate(
        state="charging",
        energy_kwh=25.0,
    )

    result = telemetry_service.create_telemetry(db, 1, telemetry)

    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
    db.rollback.assert_not_called()

    assert result.asset_id == 1
    assert result.state == "charging"
    assert result.energy_kwh == 25.0


def test_create_telemetry_rejects_missing_asset():
    db = Mock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = None

    telemetry = schemas.TelemetryCreate(
        state="charging",
        energy_kwh=25.0,
    )

    with pytest.raises(HTTPException) as exc_info:
        telemetry_service.create_telemetry(db, 999, telemetry)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Asset not found"

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_create_telemetry_rolls_back_when_commit_fails():
    db = Mock(spec=Session)

    db_asset = models.Asset(
        id=1,
        name="Battery A",
        capacity_kwh=100.0,
    )
    db.query.return_value.filter.return_value.first.return_value = db_asset
    db.commit.side_effect = RuntimeError("Database commit failed")

    telemetry = schemas.TelemetryCreate(
        state="charging",
        energy_kwh=25.0,
    )

    with pytest.raises(RuntimeError, match="Database commit failed"):
        telemetry_service.create_telemetry(db, 1, telemetry)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_called_once()
    db.refresh.assert_not_called()
