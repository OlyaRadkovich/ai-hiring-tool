#!/bin/bash
# run_worker.sh

echo "Starting main worker process in background..."
python -m backend.queue.worker &

echo "Starting health check server..."
python /app/backend/health_check_server.py