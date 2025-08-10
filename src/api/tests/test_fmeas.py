from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_create_fmea(client: TestClient):
    fmea_data = {
        "asset_id": "ASSET-001",
        "title": "Test FMEA",
        "description": "Test FMEA description",
        "version": 1
    }
    response = client.post("/fmeas/", json=fmea_data)
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "ASSET-001"
    assert data["title"] == "Test FMEA"
    assert "id" in data
    assert "created_at" in data


def test_read_fmeas(client: TestClient):
    fmea_data = {
        "asset_id": "ASSET-002",
        "title": "Test FMEA 2",
        "version": 1
    }
    client.post("/fmeas/", json=fmea_data)
    
    response = client.get("/fmeas/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_read_fmea(client: TestClient):
    fmea_data = {
        "asset_id": "ASSET-003",
        "title": "Test FMEA 3",
        "version": 1
    }
    create_response = client.post("/fmeas/", json=fmea_data)
    fmea_id = create_response.json()["id"]
    
    response = client.get(f"/fmeas/{fmea_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["asset_id"] == "ASSET-003"
    assert data["id"] == fmea_id


def test_read_fmea_not_found(client: TestClient):
    response = client.get("/fmeas/999999")
    assert response.status_code == 404


def test_update_fmea(client: TestClient):
    fmea_data = {
        "asset_id": "ASSET-004",
        "title": "Test FMEA 4",
        "version": 1
    }
    create_response = client.post("/fmeas/", json=fmea_data)
    fmea_id = create_response.json()["id"]
    
    update_data = {"title": "Updated FMEA Title"}
    response = client.put(f"/fmeas/{fmea_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated FMEA Title"
    assert data["asset_id"] == "ASSET-004"


def test_update_fmea_not_found(client: TestClient):
    update_data = {"title": "Updated Title"}
    response = client.put("/fmeas/999999", json=update_data)
    assert response.status_code == 404


def test_delete_fmea(client: TestClient):
    fmea_data = {
        "asset_id": "ASSET-005",
        "title": "Test FMEA 5",
        "version": 1
    }
    create_response = client.post("/fmeas/", json=fmea_data)
    fmea_id = create_response.json()["id"]
    
    response = client.delete(f"/fmeas/{fmea_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/fmeas/{fmea_id}")
    assert get_response.status_code == 404


def test_delete_fmea_not_found(client: TestClient):
    response = client.delete("/fmeas/999999")
    assert response.status_code == 404


def test_read_fmeas_by_asset(client: TestClient):
    asset_id = "ASSET-006"
    fmea_data = {
        "asset_id": asset_id,
        "title": "Test FMEA 6",
        "version": 1
    }
    client.post("/fmeas/", json=fmea_data)
    
    response = client.get(f"/fmeas/by-asset/{asset_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(item["asset_id"] == asset_id for item in data)