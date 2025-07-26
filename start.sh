#!/bin/bash

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Activate virtual environment
source venv310/bin/activate

# Launch FastAPI on port 8000
echo "🚀 Starting FastAPI (http://127.0.0.1:8000)..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait 2 seconds to ensure server is booted
sleep 2

# Launch Celery worker
echo "🧠 Starting Celery Worker..."
celery -A app.worker.celery_app worker --loglevel=info --pool=threads --concurrency=4