import json
import pytest
from datetime import datetime, timedelta, timezone


def test_create_asset(client):
    response = client.post(
        "/assets/",
        json={
            "name": "Battery A",
            "capacity_kwh": 100.0,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Battery A"
    assert data["capacity_kwh"] == 100.0


def test_create_telemetry(client):
    asset_response = client.post(
        "/assets/",
        json={
            "name": "Battery A",
            "capacity_kwh": 100.0,
        },
    )

    asset_id = asset_response.json()["id"]

    response = client.post(
        f"/assets/{asset_id}/telemetry/",
        json={
            "state": "charging",
            "energy_kwh": 12.5,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["asset_id"] == asset_id
    assert data["state"] == "charging"
    assert data["energy_kwh"] == 12.5
    assert data["timestamp"] is not None


def test_create_telemetry_for_missing_asset_returns_404(client):
    response = client.post(
        "/assets/9999/telemetry/",
        json={
            "state": "charging",
            "energy_kwh": 12.5,
        },
    )

    assert response.status_code == 404


def test_summary_returns_charged_and_discharged_energy(client):
    asset_response = client.post(
        "/assets/",
        json={
            "name": "Battery A",
            "capacity_kwh": 100.0,
        },
    )

    asset_id = asset_response.json()["id"]
    now = datetime.now(timezone.utc)

    for state, energy in [
        ("charging", 10.0),
        ("charging", 5.0),
        ("discharging", 3.0),
    ]:
        response = client.post(
            f"/assets/{asset_id}/telemetry/",
            json={
                "state": state,
                "energy_kwh": energy,
                "timestamp": now.isoformat(),
            },
        )

        assert response.status_code == 201

    response = client.get(f"/assets/{asset_id}/summary/")

    assert response.status_code == 200

    data = response.json()
    assert data["asset_id"] == asset_id
    assert data["total_charged_kwh"] == 15.0
    assert data["total_discharged_kwh"] == 3.0


def test_summary_for_missing_asset_returns_404(client):
    response = client.get("/assets/9999/summary/")

    assert response.status_code == 404


def test_summary_returns_zero_when_no_telemetry_exists(client):
    asset_response = client.post(
        "/assets/",
        json={
            "name": "Battery A",
            "capacity_kwh": 100.0,
        },
    )

    asset_id = asset_response.json()["id"]

    response = client.get(f"/assets/{asset_id}/summary/")

    assert response.status_code == 200

    data = response.json()
    assert data["total_charged_kwh"] == 0.0
    assert data["total_discharged_kwh"] == 0.0


def test_create_asset_rejects_invalid_payload(client):
    response = client.post("/assets/", json={})

    assert response.status_code == 422


def test_create_telemetry_rejects_invalid_payload(client):
    response = client.post(
        "/assets/1/telemetry/",
        json={},
    )

    assert response.status_code == 422


def test_create_asset_rejects_negative_capacity(client):
    response = client.post(
        "/assets/",
        json={
            "name": "Invalid Battery",
            "capacity_kwh": -100.0,
        },
    )

    assert response.status_code == 422


def test_create_asset_rejects_zero_capacity(client):
    response = client.post(
        "/assets/",
        json={
            "name": "Invalid Battery",
            "capacity_kwh": 0.0,
        },
    )

    assert response.status_code == 422


def test_create_telemetry_rejects_negative_energy(client):
    asset_response = client.post(
        "/assets/",
        json={
            "name": "Test Battery",
            "capacity_kwh": 100.0,
        },
    )

    asset_id = asset_response.json()["id"]

    response = client.post(
        f"/assets/{asset_id}/telemetry/",
        json={
            "state": "charging",
            "energy_kwh": -5.0,
        },
    )

    assert response.status_code == 422


def test_create_telemetry_rejects_invalid_state(client):
    asset_response = client.post(
        "/assets/",
        json={
            "name": "Test Battery",
            "capacity_kwh": 100.0,
        },
    )

    asset_id = asset_response.json()["id"]

    response = client.post(
        f"/assets/{asset_id}/telemetry/",
        json={
            "state": "unknown",
            "energy_kwh": 5.0,
        },
    )

    assert response.status_code == 422


def test_create_telemetry_accepts_zero_energy(client):
    asset_response = client.post(
        "/assets/",
        json={"name": "Test Battery", "capacity_kwh": 100.0},
    )
    asset_id = asset_response.json()["id"]

    response = client.post(
        f"/assets/{asset_id}/telemetry/",
        json={"state": "charging", "energy_kwh": 0.0},
    )

    assert response.status_code == 201
    assert response.json()["energy_kwh"] == 0.0


def test_create_asset_accepts_small_positive_capacity(client):
    response = client.post(
        "/assets/",
        json={"name": "Small Battery", "capacity_kwh": 0.001},
    )

    assert response.status_code == 201
    assert response.json()["capacity_kwh"] == 0.001


def test_idle_telemetry_does_not_affect_energy_summary(client):
    asset_response = client.post(
        "/assets/",
        json={"name": "Test Battery", "capacity_kwh": 100.0},
    )
    asset_id = asset_response.json()["id"]

    # Create charging telemetry.
    client.post(
        f"/assets/{asset_id}/telemetry/",
        json={"state": "charging", "energy_kwh": 10.0},
    )

    # Create discharging telemetry.
    client.post(
        f"/assets/{asset_id}/telemetry/",
        json={"state": "discharging", "energy_kwh": 4.0},
    )

    # Create idle telemetry.
    idle_response = client.post(
        f"/assets/{asset_id}/telemetry/",
        json={"state": "idle", "energy_kwh": 0.0},
    )

    assert idle_response.status_code == 201

    summary_response = client.get(
        f"/assets/{asset_id}/summary/"
    )

    assert summary_response.status_code == 200

    summary = summary_response.json()
    assert summary["total_charged_kwh"] == 10.0
    assert summary["total_discharged_kwh"] == 4.0


def test_idle_telemetry_rejects_positive_energy(client):
    asset_response = client.post(
        "/assets/",
        json={"name": "Test Battery", "capacity_kwh": 100.0},
    )
    asset_id = asset_response.json()["id"]

    response = client.post(
        f"/assets/{asset_id}/telemetry/",
        json={"state": "idle", "energy_kwh": 5.0},
    )

    assert response.status_code == 422


def test_summary_excludes_telemetry_older_than_24_hours(client):
    asset_response = client.post(
        "/assets/",
        json={"name": "Test Battery", "capacity_kwh": 100.0},
    )
    asset_id = asset_response.json()["id"]

    # Create a recent reading.
    client.post(
        f"/assets/{asset_id}/telemetry/",
        json={"state": "charging", "energy_kwh": 10.0},
    )

    # Create a reading older than 24 hours.
    old_timestamp = (
            datetime.now(timezone.utc) - timedelta(hours=25)
    ).isoformat()

    old_response = client.post(
        f"/assets/{asset_id}/telemetry/",
        json={
            "state": "charging",
            "energy_kwh": 100.0,
            "timestamp": old_timestamp,
        },
    )
    assert old_response.status_code == 201

    summary_response = client.get(
        f"/assets/{asset_id}/summary/"
    )

    assert summary_response.status_code == 200
    assert summary_response.json()["total_charged_kwh"] == 10.0


def test_summary_excludes_future_telemetry(client):
    asset_response = client.post(
        "/assets/",
        json={"name": "Test Battery", "capacity_kwh": 100.0},
    )
    asset_id = asset_response.json()["id"]

    # Create a recent reading.
    client.post(
        f"/assets/{asset_id}/telemetry/",
        json={"state": "charging", "energy_kwh": 10.0},
    )

    # Create a reading one hour in the future.
    future_timestamp = (
            datetime.now(timezone.utc) + timedelta(hours=1)
    ).isoformat()

    future_response = client.post(
        f"/assets/{asset_id}/telemetry/",
        json={
            "state": "charging",
            "energy_kwh": 100.0,
            "timestamp": future_timestamp,
        },
    )
    assert future_response.status_code == 201

    summary_response = client.get(
        f"/assets/{asset_id}/summary/"
    )

    assert summary_response.status_code == 200
    assert summary_response.json()["total_charged_kwh"] == 10.0


@pytest.mark.parametrize("invalid_value", ["NaN", "Infinity", "-Infinity"])
def test_create_asset_rejects_non_finite_capacity(client, invalid_value):
    payload = json.dumps({
        "name": "Invalid Battery",
        "capacity_kwh": invalid_value,
    })

    response = client.post(
        "/assets/",
        content=payload,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("invalid_value", ["NaN", "Infinity", "-Infinity"])
def test_create_telemetry_rejects_non_finite_energy(client, invalid_value):
    asset_response = client.post(
        "/assets/",
        json={"name": "Test Battery", "capacity_kwh": 100.0},
    )
    asset_id = asset_response.json()["id"]

    payload = json.dumps({
        "state": "charging",
        "energy_kwh": invalid_value,
    })

    response = client.post(
        f"/assets/{asset_id}/telemetry/",
        content=payload,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
