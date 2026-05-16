import pytest
from fastapi.testclient import TestClient
from device_data_service.main import app
from device_data_service.database import Base, SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

Base.metadata.create_all(bind=engine)

from device_data_service.database import get_db


def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_device():
    """Test device creation"""
    response = client.post(
        "/devices",
        json={"device_id": "test_device_1", "name": "Test Device"}
    )
    assert response.status_code == 200
    assert response.json()["device_id"] == "test_device_1"
    assert response.json()["name"] == "Test Device"


def test_get_device():
    """Test getting device"""
    # Create device first
    client.post(
        "/devices",
        json={"device_id": "test_device_2", "name": "Test Device 2"}
    )
    
    response = client.get("/devices/test_device_2")
    assert response.status_code == 200
    assert response.json()["device_id"] == "test_device_2"


def test_add_reading():
    """Test adding device reading"""
    device_id = "test_device_3"
    client.post(
        "/devices",
        json={"device_id": device_id, "name": "Test Device 3"}
    )
    
    response = client.post(
        f"/devices/{device_id}/readings",
        json={"x": 10.5, "y": 20.3, "z": 30.1}
    )
    assert response.status_code == 200
    assert response.json()["x"] == 10.5
    assert response.json()["y"] == 20.3
    assert response.json()["z"] == 30.1


def test_get_readings():
    """Test getting device readings"""
    device_id = "test_device_4"
    client.post(
        "/devices",
        json={"device_id": device_id, "name": "Test Device 4"}
    )
    
    # Add multiple readings
    for i in range(5):
        client.post(
            f"/devices/{device_id}/readings",
            json={"x": float(i), "y": float(i+1), "z": float(i+2)}
        )
    
    response = client.get(f"/devices/{device_id}/readings")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_analyze_device():
    """Test device analysis"""
    device_id = "test_device_5"
    client.post(
        "/devices",
        json={"device_id": device_id, "name": "Test Device 5"}
    )
    
    # Add readings
    for i in range(10):
        client.post(
            f"/devices/{device_id}/readings",
            json={"x": float(i), "y": float(i*2), "z": float(i*3)}
        )
    
    response = client.get(f"/analysis/device/{device_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "analysis_x" in data
    assert "analysis_y" in data
    assert "analysis_z" in data
    assert data["analysis_x"]["count"] == 10
    assert data["analysis_x"]["min"] == 0
    assert data["analysis_x"]["max"] == 9
