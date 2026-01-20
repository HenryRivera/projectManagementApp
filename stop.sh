#!/bin/bash

echo "Stopping Project Management System..."

# Detect docker compose command
if docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: Docker Compose is not installed."
    exit 1
fi

# Stop app containers
echo "Stopping app containers..."
$DOCKER_COMPOSE down

# Stop Jenkins if running
if docker ps --format '{{.Names}}' | grep -q '^jenkins$'; then
    echo "Stopping Jenkins..."
    docker stop jenkins
fi

echo ""
echo "=========================================="
echo "Application stopped!"
echo "=========================================="
echo ""
echo "To start again: ./start.sh"
echo "To remove all data: $DOCKER_COMPOSE down -v"
echo "=========================================="
