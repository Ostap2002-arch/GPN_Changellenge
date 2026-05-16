# Device Data Service - API Examples and Documentation

## Quick Start Examples

### 1. Create a Device

**Request:**
```bash
curl -X POST "http://localhost:8000/devices" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "sensor_001",
    "name": "Temperature Sensor Room 1"
  }'
```

**Response:**
```json
{
  "id": 1,
  "device_id": "sensor_001",
  "name": "Temperature Sensor Room 1",
  "created_at": "2024-05-15T10:30:00"
}
```

### 2. Add Device Reading

**Request:**
```bash
curl -X POST "http://localhost:8000/devices/sensor_001/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "x": 23.5,
    "y": 45.2,
    "z": 67.8
  }'
```

**Response:**
```json
{
  "id": 1,
  "device_id": 1,
  "x": 23.5,
  "y": 45.2,
  "z": 67.8,
  "timestamp": "2024-05-15T10:31:00"
}
```

### 3. Get Device Readings

**Request (all readings):**
```bash
curl -X GET "http://localhost:8000/devices/sensor_001/readings"
```

**Request (with time range):**
```bash
curl -X GET "http://localhost:8000/devices/sensor_001/readings?start_time=2024-05-15T00:00:00&end_time=2024-05-15T23:59:59"
```

**Response:**
```json
[
  {
    "id": 1,
    "device_id": 1,
    "x": 23.5,
    "y": 45.2,
    "z": 67.8,
    "timestamp": "2024-05-15T10:31:00"
  },
  {
    "id": 2,
    "device_id": 1,
    "x": 24.1,
    "y": 45.5,
    "z": 68.2,
    "timestamp": "2024-05-15T10:32:00"
  }
]
```

### 4. Analyze Device (All Time)

**Request:**
```bash
curl -X GET "http://localhost:8000/analysis/device/sensor_001"
```

**Response:**
```json
{
  "device_id": "sensor_001",
  "analysis_x": {
    "min": 20.5,
    "max": 30.2,
    "count": 100,
    "sum": 2450.5,
    "median": 24.8,
    "mean": 24.505
  },
  "analysis_y": {
    "min": 40.1,
    "max": 50.5,
    "count": 100,
    "sum": 4525.3,
    "median": 45.2,
    "mean": 45.253
  },
  "analysis_z": {
    "min": 60.2,
    "max": 75.1,
    "count": 100,
    "sum": 6890.7,
    "median": 68.9,
    "mean": 68.907
  },
  "period_start": null,
  "period_end": null
}
```

### 5. Analyze Device (Last 24 Hours)

**Request:**
```bash
curl -X GET "http://localhost:8000/analysis/device/sensor_001/last-24h"
```

**Response:** (same structure as above with period_start and period_end set)

### 6. Analyze Device (Period)

**Request:**
```bash
curl -X GET "http://localhost:8000/analysis/device/sensor_001?start_time=2024-05-10T00:00:00&end_time=2024-05-15T23:59:59"
```

### 7. Create User

**Request:**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

### 8. Get User Information

**Request:**
```bash
curl -X GET "http://localhost:8000/users/1"
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

### 9. Analyze User Devices

**Request:**
```bash
curl -X GET "http://localhost:8000/analysis/user/1/devices"
```

**Response:**
```json
{
  "devices": [
    {
      "device_id": "sensor_001",
      "analysis_x": {
        "min": 20.5,
        "max": 30.2,
        "count": 100,
        "sum": 2450.5,
        "median": 24.8,
        "mean": 24.505
      },
      "analysis_y": {...},
      "analysis_z": {...}
    }
  ],
  "total_analysis_x": {
    "min": 20.5,
    "max": 30.2,
    "count": 150,
    "sum": 3675.75,
    "median": 24.9,
    "mean": 24.505
  },
  "total_analysis_y": {...},
  "total_analysis_z": {...}
}
```

### 10. List All Devices

**Request:**
```bash
curl -X GET "http://localhost:8000/devices"
```

**Response:**
```json
[
  {
    "id": 1,
    "device_id": "sensor_001",
    "name": "Temperature Sensor Room 1",
    "created_at": "2024-05-15T10:30:00"
  },
  {
    "id": 2,
    "device_id": "sensor_002",
    "name": "Humidity Sensor Room 1",
    "created_at": "2024-05-15T10:31:00"
  }
]
```

## Python Client Example

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class DeviceDataClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def create_device(self, device_id: str, name: str):
        """Create a new device"""
        response = requests.post(
            f"{self.base_url}/devices",
            json={"device_id": device_id, "name": name}
        )
        return response.json()
    
    def add_reading(self, device_id: str, x: float, y: float, z: float):
        """Add a reading to device"""
        response = requests.post(
            f"{self.base_url}/devices/{device_id}/readings",
            json={"x": x, "y": y, "z": z}
        )
        return response.json()
    
    def get_readings(self, device_id: str, start_time=None, end_time=None):
        """Get device readings"""
        params = {}
        if start_time:
            params['start_time'] = start_time.isoformat()
        if end_time:
            params['end_time'] = end_time.isoformat()
        
        response = requests.get(
            f"{self.base_url}/devices/{device_id}/readings",
            params=params
        )
        return response.json()
    
    def analyze_device(self, device_id: str):
        """Analyze device (all time)"""
        response = requests.get(
            f"{self.base_url}/analysis/device/{device_id}"
        )
        return response.json()
    
    def analyze_device_last_24h(self, device_id: str):
        """Analyze device (last 24 hours)"""
        response = requests.get(
            f"{self.base_url}/analysis/device/{device_id}/last-24h"
        )
        return response.json()

# Usage example
if __name__ == "__main__":
    client = DeviceDataClient()
    
    # Create device
    device = client.create_device("sensor_001", "Temperature Sensor")
    print(f"Created device: {device}")
    
    # Add readings
    for i in range(10):
        reading = client.add_reading("sensor_001", 20 + i*0.5, 45 + i*0.3, 65 + i*0.2)
        print(f"Added reading: {reading}")
    
    # Get readings
    readings = client.get_readings("sensor_001")
    print(f"Got {len(readings)} readings")
    
    # Analyze device
    analysis = client.analyze_device("sensor_001")
    print(f"Analysis: {json.dumps(analysis, indent=2)}")
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Device already exists"
}
```

### 404 Not Found
```json
{
  "detail": "Device not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## High-Volume Data Ingestion Pattern

For high-volume data ingestion, consider batching:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def batch_add_readings(device_id: str, readings_list: list):
    """Add multiple readings efficiently"""
    for reading in readings_list:
        response = requests.post(
            f"{BASE_URL}/devices/{device_id}/readings",
            json=reading
        )
        if response.status_code != 200:
            print(f"Error adding reading: {response.text}")

# Example: Add 1000 readings
readings = [
    {"x": 20 + i*0.1, "y": 45 + i*0.05, "z": 65 + i*0.02}
    for i in range(1000)
]

batch_add_readings("sensor_001", readings)
```

## Performance Tips

1. **Batch Operations**: Group multiple readings together for better performance
2. **Use Time Ranges**: When querying analysis, use time ranges to reduce computation
3. **Cache Results**: Store analysis results if they're frequently accessed
4. **Async Tasks**: Use Celery for heavy analysis computations
5. **Database Indexing**: Ensure database has indexes on device_id and timestamp

## Rate Limiting (Future Enhancement)

Recommended rate limits:
- Device creation: 10 per minute per IP
- Reading submission: 1000 per minute per device
- Analysis queries: 100 per minute per user

