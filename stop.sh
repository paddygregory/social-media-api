#!/bin/bash

echo "Stopping FastAPI server..."
pkill -f "uvicorn.*app.main"

echo "Stopping Celery worker..."
pkill -f "celery.*worker"

echo "All services stopped!" 