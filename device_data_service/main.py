from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from starlette.concurrency import run_in_threadpool
from device_data_service.database import engine, get_db, Base
from device_data_service.models import Device, DeviceReading
from device_data_service.schemas import (
    DeviceReadingCreate, DeviceReadingResponse, AnalysisResponse,
    AggregatedAnalysisResponse, DeviceCreate, DeviceResponse,
    UserCreate, UserResponse, TaskResponse
)
from device_data_service.services import (
    DeviceService, ReadingService, AnalysisService, UserService
)
from device_data_service.celery_app import analyze_device_task, celery_app, generate_report_task

# Create tables
Base.metadata.create_all(bind=engine)

# Define OpenAPI tags for organizing endpoints in Swagger UI
tags_metadata = [
    {
        "name": "Health",
        "description": "System health and status checks",
    },
    {
        "name": "Devices",
        "description": "CRUD operations for managing devices",
    },
    {
        "name": "Readings",
        "description": "Device readings management - add and retrieve sensor data",
    },
    {
        "name": "Analysis - Device",
        "description": "Analyze individual device readings with statistical calculations",
    },
    {
        "name": "Users",
        "description": "User management operations",
    },
    {
        "name": "Analysis - User",
        "description": "Analyze all devices for a specific user with aggregated statistics",
    },
    {
        "name": "Tasks",
        "description": "Async task monitoring and status retrieval",
    },
]

app = FastAPI(
    title="Device Data Service API")


# ============= Health Check =============
@app.get("/health", tags=["Health"], summary="Health Check")
async def health_check():
    """
    Check if the API is running and healthy.
    
    Returns a simple status message confirming the service is operational.
    """
    return {"status": "ok"}


# ============= Device Endpoints =============
@app.post("/devices", response_model=DeviceResponse, tags=["Devices"], summary="Create New Device")
async def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """
    Create a new device in the system.
    
    **Parameters:**
    - **device_id** (string): Unique identifier for the device (must be unique)
    - **name** (string): Human-readable name for the device
    
    **Returns:** Created device object with ID and creation timestamp
    
    **Example:**
    ```json
    {
        "device_id": "sensor_room_1",
        "name": "Sensor Room 1"
    }
    ```
    """
    # DeviceService uses blocking SQLAlchemy sessions — run in a threadpool
    existing = await run_in_threadpool(DeviceService.get_device_by_id, db, device.device_id)
    if existing:
        raise HTTPException(status_code=400, detail="Device already exists")

    db_device = await run_in_threadpool(DeviceService.create_device, db, device.device_id, device.name)
    return db_device


@app.get("/devices", response_model=list[DeviceResponse], tags=["Devices"], summary="List All Devices")
async def list_devices(db: Session = Depends(get_db)):
    """
    Get a list of all registered devices.
    
    **Returns:** Array of all device objects
    """
    devices = await run_in_threadpool(DeviceService.get_all_devices, db)
    return devices


@app.get("/devices/{device_id}", response_model=DeviceResponse, tags=["Devices"], summary="Get Device Details")
async def get_device(device_id: str, db: Session = Depends(get_db)):
    """
    Retrieve details for a specific device by its ID.
    
    **Parameters:**
    - **device_id** (path): The unique identifier of the device
    
    **Returns:** Device object if found
    
    **Errors:**
    - 404: Device not found
    """
    device = await run_in_threadpool(DeviceService.get_device_by_id, db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@app.delete("/devices/{device_id}", tags=["Devices"], summary="Delete Device")
async def delete_device(device_id: str, db: Session = Depends(get_db)):
    """
    Delete a device and all its associated readings.
    
    **Parameters:**
    - **device_id** (path): The unique identifier of the device to delete
    
    **Returns:** Success message
    
    **Errors:**
    - 404: Device not found
    """
    deleted = await run_in_threadpool(DeviceService.delete_device, db, device_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device deleted successfully"}


# ============= Device Reading Endpoints =============
@app.post("/devices/{device_id}/readings", response_model=DeviceReadingResponse, tags=["Readings"], summary="Add Device Reading")
async def add_reading(device_id: str, reading: DeviceReadingCreate, db: Session = Depends(get_db)):
    """
    Add a new reading to a device.
    
    Sensor readings contain x, y, z values (e.g., accelerometer or gyroscope data).
    If the device doesn't exist, it will be created automatically.
    
    **Parameters:**
    - **device_id** (path): The device to record reading for
    - **reading** (body): Object containing x, y, z float values
    
    **Returns:** Created reading object with timestamp
    
    **Example:**
    ```json
    {
        "x": 45.5,
        "y": 32.1,
        "z": 28.9
    }
    ```
    """
    db_reading = await run_in_threadpool(ReadingService.save_reading, db, device_id, reading.x, reading.y, reading.z)
    result = {
        "id": db_reading.id,
        "device_id": db_reading.device_id,
        "x": db_reading.x,
        "y": db_reading.y,
        "z": db_reading.z,
        "timestamp": db_reading.timestamp
    }
    return result


@app.get("/devices/{device_id}/readings", response_model=list[DeviceReadingResponse], tags=["Readings"], summary="Get Device Readings")
async def get_readings(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="Filter readings from this time (ISO 8601 format)"),
    end_time: Optional[datetime] = Query(None, description="Filter readings until this time (ISO 8601 format)"),
    skip: int = Query(0, ge=0, description="Number of readings to skip (offset)"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of readings to return (max 10000)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve readings for a device, optionally filtered by time range with pagination.
    
    **Parameters:**
    - **device_id** (path): The device to retrieve readings for
    - **start_time** (query, optional): Beginning of time range (ISO 8601 format)
    - **end_time** (query, optional): End of time range (ISO 8601 format)
    - **skip** (query, optional): Number of records to skip (default: 0)
    - **limit** (query, optional): Maximum records to return (default: 1000, max: 10000)
    
    **Returns:** Array of reading objects (paginated)
    
    **Example Query:**
    ```
    /devices/sensor_room_1/readings?start_time=2024-01-01T00:00:00&end_time=2024-01-31T23:59:59&skip=0&limit=100
    ```
    """
    readings = await run_in_threadpool(ReadingService.get_readings, db, device_id, start_time, end_time, skip, limit)
    results = []
    for r in readings:
        results.append({
            "id": r.id,
            "device_id": r.device_id,
            "x": r.x,
            "y": r.y,
            "z": r.z,
            "timestamp": r.timestamp
        })
    return results


# ============= Analysis Endpoints =============
@app.get("/analysis/device/{device_id}", response_model=TaskResponse, tags=["Analysis - Device"], summary="Analyze Device (Async)")
async def analyze_device(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="Start of analysis period (ISO 8601)"),
    end_time: Optional[datetime] = Query(None, description="End of analysis period (ISO 8601)")
):
    """
    Schedule an asynchronous analysis task for device readings.
    
    This endpoint returns immediately with a task ID. Use the `/tasks/{task_id}` endpoint
    to check the status and retrieve results.
    
    **Parameters:**
    - **device_id** (path): Device to analyze
    - **start_time** (query, optional): Start of period to analyze
    - **end_time** (query, optional): End of period to analyze
    
    **Returns:** Task ID for monitoring progress
    """
    task = analyze_device_task.delay(
        device_id,
        start_time.isoformat() if start_time else None,
        end_time.isoformat() if end_time else None
    )
    return {"task_id": task.id, "status": task.status}


@app.get("/analysis/device/{device_id}/last-24h", response_model=TaskResponse, tags=["Analysis - Device"], summary="Analyze Last 24h (Async)")
async def analyze_device_last_24h(device_id: str):
    """
    Schedule analysis for device readings from the last 24 hours (async).
    
    **Parameters:**
    - **device_id** (path): Device to analyze
    
    **Returns:** Task ID for monitoring progress
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    task = analyze_device_task.delay(device_id, start_time.isoformat(), end_time.isoformat())
    return {"task_id": task.id, "status": task.status}


@app.get("/analysis/device/{device_id}/last-7d", response_model=TaskResponse, tags=["Analysis - Device"], summary="Analyze Last 7 Days (Async)")
async def analyze_device_last_7d(device_id: str):
    """
    Schedule analysis for device readings from the last 7 days (async).
    
    **Parameters:**
    - **device_id** (path): Device to analyze
    
    **Returns:** Task ID for monitoring progress
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)
    task = analyze_device_task.delay(device_id, start_time.isoformat(), end_time.isoformat())
    return {"task_id": task.id, "status": task.status}



# ============= User Endpoints =============
@app.post("/users", response_model=UserResponse, tags=["Users"], summary="Create User")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the system.
    
    Users can own multiple devices and their readings can be analyzed together.
    
    **Parameters:**
    - **username** (string): Unique username
    - **email** (string): User's email address
    
    **Returns:** Created user object
    
    **Example:**
    ```json
    {
        "username": "john_doe",
        "email": "john@example.com"
    }
    ```
    """
    existing = await run_in_threadpool(UserService.get_user_by_username, db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = await run_in_threadpool(UserService.create_user, db, user.username, user.email)
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"], summary="Get User")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve user information by ID.
    
    **Parameters:**
    - **user_id** (path): The numeric user ID
    
    **Returns:** User object
    
    **Errors:**
    - 404: User not found
    """
    user = await run_in_threadpool(UserService.get_user, db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============= User Analysis Endpoints =============
@app.get("/analysis/user/{user_id}/devices", response_model=TaskResponse, tags=["Analysis - User"], summary="Analyze User Devices (Async)")
async def analyze_user_devices(
    user_id: int,
    start_time: Optional[datetime] = Query(None, description="Start of analysis period (ISO 8601)"),
    end_time: Optional[datetime] = Query(None, description="End of analysis period (ISO 8601)")
):
    """
    Schedule analysis for all devices belonging to a user (async).
    
    Provides aggregated statistics across all user devices.
    
    **Parameters:**
    - **user_id** (path): The user ID
    - **start_time** (query, optional): Start of analysis period
    - **end_time** (query, optional): End of analysis period
    
    **Returns:** Task ID for monitoring progress
    """
    task = generate_report_task.delay(
        user_id,
        start_time.isoformat() if start_time else None,
        end_time.isoformat() if end_time else None
    )
    return {"task_id": task.id, "status": task.status}


@app.get("/analysis/user/{user_id}/devices/last-24h", response_model=TaskResponse, tags=["Analysis - User"], summary="Analyze User Devices Last 24h (Async)")
async def analyze_user_devices_last_24h(user_id: int):
    """
    Schedule analysis for all user devices from last 24 hours (async).
    
    **Parameters:**
    - **user_id** (path): The user ID
    
    **Returns:** Task ID for monitoring progress
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    task = generate_report_task.delay(user_id, start_time.isoformat(), end_time.isoformat())
    return {"task_id": task.id, "status": task.status}


@app.get("/tasks/{task_id}", tags=["Tasks"], summary="Get Task Status")
async def get_task_status(task_id: str):
    """
    Check the status and result of an async task.
    
    Use this endpoint to poll the status of tasks created by async endpoints
    (endpoints that return a `TaskResponse`).
    
    **Parameters:**
    - **task_id** (path): The task ID returned by an async endpoint
    
    **Returns:** Task status and result (if completed)
    
    **Status Values:**
    - **PENDING**: Task is waiting to be executed
    - **STARTED**: Task execution has begun
    - **SUCCESS**: Task completed successfully (result field contains the data)
    - **FAILURE**: Task failed (error field contains the error message)
    
    **Example Usage:**
    ```
    1. Call GET /analysis/device/{device_id} → get task_id
    2. Poll GET /tasks/{task_id} until status is SUCCESS
    3. Extract result from the response
    ```
    """
    # AsyncResult interacts with the result backend (blocking) — run in threadpool
    def _fetch_task():
        r = celery_app.AsyncResult(task_id)
        resp = {"task_id": task_id, "status": r.status}
        if r.status == "SUCCESS":
            resp["result"] = r.result
        elif r.status == "FAILURE":
            resp["error"] = str(r.result)
        try:
            r.forget()
        except Exception:
            pass
        return resp

    response = await run_in_threadpool(_fetch_task)
    return response


if __name__ == "__main__":
    import uvicorn
    from device_data_service.config import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port)
