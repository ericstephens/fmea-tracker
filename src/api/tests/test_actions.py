from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_failure_mode_id(client: TestClient):
    fmea_data = {
        "asset_id": "ACTION-ASSET-001",
        "title": "Test FMEA for Actions",
        "version": 1
    }
    fmea_response = client.post("/fmeas/", json=fmea_data)
    fmea_id = fmea_response.json()["id"]
    
    failure_mode_data = {
        "fmea_id": fmea_id,
        "name": "Test Failure Mode for Actions"
    }
    fm_response = client.post("/failure-modes/", json=failure_mode_data)
    return fm_response.json()["id"]


def test_create_action(client: TestClient, test_failure_mode_id: int):
    action_data = {
        "failure_mode_id": test_failure_mode_id,
        "description": "Test corrective action",
        "owner": "John Doe",
        "status": "open"
    }
    response = client.post("/actions/", json=action_data)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test corrective action"
    assert data["owner"] == "John Doe"
    assert data["status"] == "open"
    assert "id" in data


def test_update_action(client: TestClient, test_failure_mode_id: int):
    action_data = {
        "failure_mode_id": test_failure_mode_id,
        "description": "Test action to update",
        "status": "open"
    }
    create_response = client.post("/actions/", json=action_data)
    action_id = create_response.json()["id"]
    
    update_data = {"status": "in_progress", "owner": "Jane Smith"}
    response = client.put(f"/actions/{action_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["owner"] == "Jane Smith"
    assert data["description"] == "Test action to update"


def test_update_action_not_found(client: TestClient):
    update_data = {"status": "closed"}
    response = client.put("/actions/999999", json=update_data)
    assert response.status_code == 404


def test_delete_action(client: TestClient, test_failure_mode_id: int):
    action_data = {
        "failure_mode_id": test_failure_mode_id,
        "description": "Test action to delete"
    }
    create_response = client.post("/actions/", json=action_data)
    action_id = create_response.json()["id"]
    
    response = client.delete(f"/actions/{action_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Action deleted successfully"


def test_delete_action_not_found(client: TestClient):
    response = client.delete("/actions/999999")
    assert response.status_code == 404


def test_read_actions_by_failure_mode(client: TestClient, test_failure_mode_id: int):
    action_data = {
        "failure_mode_id": test_failure_mode_id,
        "description": "Test action for listing"
    }
    client.post("/actions/", json=action_data)
    
    response = client.get(f"/actions/by-failure-mode/{test_failure_mode_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(item["failure_mode_id"] == test_failure_mode_id for item in data)