from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_fmea_id(client: TestClient):
    fmea_data = {
        "asset_id": "FM-ASSET-001",
        "title": "Test FMEA for Failure Modes",
        "version": 1
    }
    response = client.post("/fmeas/", json=fmea_data)
    return response.json()["id"]


def test_create_failure_mode(client: TestClient, test_fmea_id: int):
    failure_mode_data = {
        "fmea_id": test_fmea_id,
        "name": "Test Failure Mode",
        "severity": 5,
        "occurrence": 3,
        "detection": 4
    }
    response = client.post("/failure-modes/", json=failure_mode_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Failure Mode"
    assert data["severity"] == 5
    assert data["occurrence"] == 3
    assert data["detection"] == 4
    assert data["rpn"] == 60  # 5 * 3 * 4
    assert "id" in data


def test_read_failure_mode(client: TestClient, test_fmea_id: int):
    failure_mode_data = {
        "fmea_id": test_fmea_id,
        "name": "Test Failure Mode 2",
        "severity": 7
    }
    create_response = client.post("/failure-modes/", json=failure_mode_data)
    failure_mode_id = create_response.json()["id"]
    
    response = client.get(f"/failure-modes/{failure_mode_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Failure Mode 2"
    assert data["id"] == failure_mode_id


def test_read_failure_mode_not_found(client: TestClient):
    response = client.get("/failure-modes/999999")
    assert response.status_code == 404


def test_update_failure_mode(client: TestClient, test_fmea_id: int):
    failure_mode_data = {
        "fmea_id": test_fmea_id,
        "name": "Test Failure Mode 3",
        "severity": 2
    }
    create_response = client.post("/failure-modes/", json=failure_mode_data)
    failure_mode_id = create_response.json()["id"]
    
    update_data = {"severity": 8, "occurrence": 2}
    response = client.put(f"/failure-modes/{failure_mode_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == 8
    assert data["occurrence"] == 2
    assert data["rpn"] == 160  # 8 * 2 * 10 (default detection)


def test_update_failure_mode_not_found(client: TestClient):
    update_data = {"severity": 5}
    response = client.put("/failure-modes/999999", json=update_data)
    assert response.status_code == 404


def test_delete_failure_mode(client: TestClient, test_fmea_id: int):
    failure_mode_data = {
        "fmea_id": test_fmea_id,
        "name": "Test Failure Mode 4"
    }
    create_response = client.post("/failure-modes/", json=failure_mode_data)
    failure_mode_id = create_response.json()["id"]
    
    response = client.delete(f"/failure-modes/{failure_mode_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/failure-modes/{failure_mode_id}")
    assert get_response.status_code == 404


def test_delete_failure_mode_not_found(client: TestClient):
    response = client.delete("/failure-modes/999999")
    assert response.status_code == 404


def test_read_failure_modes_by_fmea(client: TestClient, test_fmea_id: int):
    failure_mode_data = {
        "fmea_id": test_fmea_id,
        "name": "Test Failure Mode 5"
    }
    client.post("/failure-modes/", json=failure_mode_data)
    
    response = client.get(f"/failure-modes/by-fmea/{test_fmea_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(item["fmea_id"] == test_fmea_id for item in data)