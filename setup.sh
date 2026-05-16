#!/bin/bash

# Script to setup and run the Device Data Service

set -e

echo "================================"
echo "Device Data Service Setup"
echo "================================"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    pip install poetry
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Create database
echo "Setting up database..."
python -c "from device_data_service.database import Base, engine; Base.metadata.create_all(bind=engine)"

echo ""
echo "================================"
echo "✓ Setup completed successfully!"
echo "================================"
echo ""
echo "To start the API server, run:"
echo "  poetry run python -m uvicorn device_data_service.main:app --reload"
echo ""
echo "To run with Docker Compose, use:"
echo "  docker-compose up"
echo ""
echo "To run load tests, use:"
echo "  poetry run locust -f tests/load_test.py --host=http://localhost:8000"
echo ""
