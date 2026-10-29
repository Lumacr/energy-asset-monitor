
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.services import summary_service


def test_get_asset_summary_returns_energy_totals():
    db = Mock(spec=Session)
    db_asset = models.Asset(
        id=1,
        name="Battery A",
        capacity_kwh=100.0,
    )

    db.query.return_value.filter.return_value.first.return_value = db_asset

    db.query.return_value.filter.return_value.scalar.side_effect = [
        25.0,
        10.0,
    ]

    result = summary_service.get_asset_summary(db, 1)

    assert result.asset_id == 1
    assert result.total_charged_kwh == 25.0
    assert result.total_discharged_kwh == 10.0


def test_get_asset_summary_returns_zero_when_no_telemetry_exists():
    db = Mock(spec=Session)
    db_asset = models.Asset(
        id=1,
        name="Battery A",
        capacity_kwh=100.0,
    )

    db.query.return_value.filter.return_value.first.return_value = db_asset

    db.query.return_value.filter.return_value.scalar.side_effect = [
        None,
        None,
    ]

    result = summary_service.get_asset_summary(db, 1)

    assert result.total_charged_kwh == 0.0
    assert result.total_discharged_kwh == 0.0


def test_get_asset_summary_rejects_missing_asset():
    db = Mock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        summary_service.get_asset_summary(db, 999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Asset not found"

    assert db.query.return_value.filter.return_value.scalar.call_count == 0
