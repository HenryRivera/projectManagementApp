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

# Remove any orphaned containers to prevent conflicts
echo "Cleaning up old containers..."
docker rm -f project-management-backend project-management-frontend project-management-nginx 2>/dev/null || true

# Build and start app containers
echo "Building and starting app containers..."
$DOCKER_COMPOSE up -d --build

# Start Jenkins if it exists
if docker ps -a --format '{{.Names}}' | grep -q '^jenkins$'; then
    echo "Starting Jenkins..."
    docker start jenkins
    JENKINS_RUNNING=true
else
    echo "Note: Jenkins container not found. Skipping Jenkins startup."
    echo "To set up Jenkins, see the CI/CD section in README.md"
    JENKINS_RUNNING=false
fi

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
if [ "$JENKINS_RUNNING" = true ]; then
    echo "Jenkins: http://localhost:8081"
fi
echo ""
echo "To view logs: $DOCKER_COMPOSE logs -f"
echo "To stop app: $DOCKER_COMPOSE down"
if [ "$JENKINS_RUNNING" = true ]; then
    echo "To stop Jenkins: docker stop jenkins"
fi
echo "=========================================="
