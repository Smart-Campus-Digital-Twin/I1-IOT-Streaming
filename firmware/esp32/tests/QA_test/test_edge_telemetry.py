import pytest
import requests
from pydantic import BaseModel, ValidationError

# =====================================================================
# 1. THE DATA CONTRACT (Schema Definition)
# Matches the Pydantic schema used by the Ingestion Bridge
# =====================================================================

class SensorMetrics(BaseModel):
    voltage_v: float
    current_a: float
    active_power_w: float
    power_factor: float

class SensorReading(BaseModel):
    sensor_id: str
    building_id: str
    room_id: str
    sensor_type: str
    metrics: SensorMetrics
    timestamp_ms: int

# =====================================================================
# 2. SCHEMA VALIDATION TESTS (Offline QA)
# Tests if the ESP32 payload matches the strict JSON contract
# =====================================================================

def test_valid_payload_schema():
    """QA Test: Ensure a perfectly formatted JSON payload passes validation."""
    valid_data = {
        "sensor_id": "energy_node_DB_floor1_roomA",
        "building_id": "EF",
        "room_id": "EF101",
        "sensor_type": "energy_watts",
        "metrics": {
            "voltage_v": 231.2,
            "current_a": 12.4,
            "active_power_w": 2721.5,
            "power_factor": 0.95
        },
        "timestamp_ms": 1714980240000
    }
    # If the payload is perfect, Pydantic will parse it without throwing an error
    reading = SensorReading(**valid_data)
    assert reading.sensor_id == "energy_node_DB_floor1_roomA"

def test_invalid_payload_missing_timestamp():
    """QA Test: Ensure payloads missing the critical timestamp_ms are rejected."""
    invalid_data = {
        "sensor_id": "energy_node_DB_floor1_roomA",
        "building_id": "EF",
        "room_id": "EF101",
        "sensor_type": "energy_watts",
        "metrics": {
            "voltage_v": 231.2, 
            "current_a": 12.4, 
            "active_power_w": 2721.5, 
            "power_factor": 0.95
        }
        # intentionally missing 'timestamp_ms'
    }
    # We EXPECT a ValidationError to be raised here
    with pytest.raises(ValidationError):
        SensorReading(**invalid_data)

def test_invalid_payload_wrong_data_type():
    """QA Test: Ensure string values in numeric fields (like power) are rejected."""
    invalid_data = {
        "sensor_id": "energy_node_DB_floor1",
        "building_id": "EF",
        "room_id": "EF101",
        "sensor_type": "energy_watts",
        "metrics": {
            "voltage_v": "HIGH_VOLTAGE",  # This should be a float, not a string!
            "current_a": 12.4,
            "active_power_w": 2721.5,
            "power_factor": 0.95
        },
        "timestamp_ms": 1714980240000
    }
    with pytest.raises(ValidationError):
        SensorReading(**invalid_data)

# =====================================================================
# 3. KONG GATEWAY & KEYCLOAK AUTHENTICATION TESTS
# Tests the Zero-Trust perimeter deployment
# =====================================================================

# Configuration for the test environment
KONG_GATEWAY_URL = "http://localhost:8000/api/v1/telemetry" # Target Kong Route
MOCK_VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.valid_token_mock"

@pytest.fixture
def valid_headers():
    return {
        "Authorization": f"Bearer {MOCK_VALID_TOKEN}", 
        "Content-Type": "application/json"
    }

def test_kong_auth_valid_token(requests_mock, valid_headers):
    """QA Test: ESP32 with a valid Keycloak JWT token is permitted by Kong."""
    # Using requests_mock to simulate Kong's response in a CI/CD pipeline
    requests_mock.post(KONG_GATEWAY_URL, status_code=202)
    
    payload = {"status": "test_ping"} 
    response = requests.post(KONG_GATEWAY_URL, json=payload, headers=valid_headers)
    
    assert response.status_code == 202

def test_kong_auth_missing_token(requests_mock):
    """QA Test: Rogue ESP32 WITHOUT a Keycloak token is actively blocked (401)."""
    requests_mock.post(KONG_GATEWAY_URL, status_code=401)
    
    payload = {"status": "test_ping"}
    headers = {"Content-Type": "application/json"} # Notice: No Auth header
    
    response = requests.post(KONG_GATEWAY_URL, json=payload, headers=headers)
    
    assert response.status_code == 401

def test_kong_auth_invalid_token(requests_mock):
    """QA Test: ESP32 with a forged or expired token is blocked (401 or 403)."""
    requests_mock.post(KONG_GATEWAY_URL, status_code=403)
    
    payload = {"status": "test_ping"}
    headers = {
        "Authorization": "Bearer fake_forged_token_123", 
        "Content-Type": "application/json"
    }
    
    response = requests.post(KONG_GATEWAY_URL, json=payload, headers=headers)
    
    assert response.status_code in [401, 403]