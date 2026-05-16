@echo off
REM Script to setup and run the Device Data Service on Windows

echo ================================
echo Device Data Service Setup
echo ================================

REM Check if poetry is installed
poetry --version >nul 2>&1
if errorlevel 1 (
    echo Installing Poetry...
    pip install poetry
)

REM Install dependencies
echo Installing dependencies...
poetry install

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
)

REM Create database
echo Setting up database...
python -c "from device_data_service.database import Base, engine; Base.metadata.create_all(bind=engine)"

echo.
echo ================================
echo Setup completed successfully!
echo ================================
echo.
echo To start the API server, run:
echo   poetry run python -m uvicorn device_data_service.main:app --reload
echo.
echo To run with Docker Compose, use:
echo   docker-compose up
echo.
echo To run load tests, use:
echo   poetry run locust -f tests/load_test.py --host=http://localhost:8000
echo.
pause
