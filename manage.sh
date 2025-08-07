#!/bin/bash

# FMEA Tracker Application Management Script
# This script handles start, stop, restart operations for the application

set -e

# Set environment variables
export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export CONDA_ENV_NAME="fmea-tracker"

# Function to check if conda environment exists
check_conda_env() {
    if ! conda info --envs | grep -q "$CONDA_ENV_NAME"; then
        echo "Conda environment '$CONDA_ENV_NAME' does not exist. Creating it..."
        conda env create -f "$PROJECT_ROOT/environment.yaml"
    else
        echo "Updating conda environment..."
        conda env update -f "$PROJECT_ROOT/environment.yaml"
    fi
}

# Function to start PostgreSQL container
start_db() {
    echo "Starting PostgreSQL container..."
    if ! podman container exists fmea-postgres; then
        podman run -d \
            --name fmea-postgres \
            -e POSTGRES_USER=fmea \
            -e POSTGRES_PASSWORD=fmea_password \
            -e POSTGRES_DB=fmea_db \
            -p 5432:5432 \
            postgres:15
        
        # Wait for PostgreSQL to start
        echo "Waiting for PostgreSQL to start..."
        sleep 5
    else
        podman start fmea-postgres
    fi
}

# Function to start API server
start_api() {
    echo "Starting API server..."
    conda run -n "$CONDA_ENV_NAME" uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
    echo $! > "$PROJECT_ROOT/.api.pid"
}

# Function to start Frontend
start_frontend() {
    echo "Starting Frontend..."
    cd "$PROJECT_ROOT/src/frontend" && npm start &
    echo $! > "$PROJECT_ROOT/.frontend.pid"
}

# Function to stop API server
stop_api() {
    if [ -f "$PROJECT_ROOT/.api.pid" ]; then
        echo "Stopping API server..."
        PID=$(cat "$PROJECT_ROOT/.api.pid")
        if ps -p $PID > /dev/null; then
            kill $PID
        fi
        rm "$PROJECT_ROOT/.api.pid"
    fi
}

# Function to stop Frontend
stop_frontend() {
    if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
        echo "Stopping Frontend..."
        PID=$(cat "$PROJECT_ROOT/.frontend.pid")
        if ps -p $PID > /dev/null; then
            kill $PID
        fi
        rm "$PROJECT_ROOT/.frontend.pid"
    fi
}

# Function to stop PostgreSQL container
stop_db() {
    echo "Stopping PostgreSQL container..."
    if podman container exists fmea-postgres; then
        podman stop fmea-postgres
    fi
}

# Start all components
start() {
    check_conda_env
    start_db
    start_api
    start_frontend
    echo "All components started successfully!"
}

# Stop all components
stop() {
    stop_frontend
    stop_api
    stop_db
    echo "All components stopped successfully!"
}

# Restart all components
restart() {
    echo "Restarting all components..."
    stop
    start
}

# Main script logic
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
