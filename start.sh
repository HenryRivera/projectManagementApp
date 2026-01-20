#!/bin/bash

echo "Starting Project Management System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Detect docker compose command (v2 uses 'docker compose', v1 uses 'docker-compose')
if docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

# Build and start containers
echo "Building and starting containers..."
$DOCKER_COMPOSE up -d --build

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 5

# Initialize database
echo "Initializing database with sample data..."
$DOCKER_COMPOSE exec -T backend python init_db.py

echo ""
echo "=========================================="
echo "Application is ready!"
echo "=========================================="
echo "Frontend: http://localhost"
echo "Backend API: http://localhost/api"
echo "API Docs: http://localhost/api/docs"
echo ""
echo "To view logs: $DOCKER_COMPOSE logs -f"
echo "To stop: $DOCKER_COMPOSE down"
echo "=========================================="
