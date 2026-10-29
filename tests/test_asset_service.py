
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app import schemas
from app.services import asset_service


def test_create_asset_commits_and_returns_asset():
    db = Mock(spec=Session)
    asset = schemas.AssetCreate(
        name="Battery A",
        capacity_kwh=100.0,
    )

    result = asset_service.create_asset(db, asset)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
    db.rollback.assert_not_called()

    assert result.name == "Battery A"
    assert result.capacity_kwh == 100.0


def test_create_asset_rolls_back_when_commit_fails():
    db = Mock(spec=Session)
    db.commit.side_effect = RuntimeError("Database commit failed")

    asset = schemas.AssetCreate(
        name="Battery A",
        capacity_kwh=100.0,
    )

    with pytest.raises(
        RuntimeError,
        match="Database commit failed",
    ):
        asset_service.create_asset(db, asset)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_called_once()
    db.refresh.assert_not_called()
