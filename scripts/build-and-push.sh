#!/bin/bash

# Script to build and push Docker images to Docker Hub
# Usage: ./scripts/build-and-push.sh [your-dockerhub-username] [version]

set -e

DOCKER_USERNAME=${1:-"your-username"}
VERSION=${2:-"latest"}

if [ "$DOCKER_USERNAME" == "your-username" ]; then
    echo "Error: Please provide your Docker Hub username"
    echo "Usage: ./scripts/build-and-push.sh [your-dockerhub-username] [version]"
    exit 1
fi

echo "Building and pushing images to Docker Hub..."
echo "Username: $DOCKER_USERNAME"
echo "Version: $VERSION"
echo ""

# Build backend image
echo "Building backend image..."
docker build -f backend/Dockerfile.prod -t ${DOCKER_USERNAME}/project-management-backend:${VERSION} ./backend
docker tag ${DOCKER_USERNAME}/project-management-backend:${VERSION} ${DOCKER_USERNAME}/project-management-backend:latest

# Build frontend image
echo "Building frontend image..."
docker build -f frontend/Dockerfile.prod -t ${DOCKER_USERNAME}/project-management-frontend:${VERSION} ./frontend
docker tag ${DOCKER_USERNAME}/project-management-frontend:${VERSION} ${DOCKER_USERNAME}/project-management-frontend:latest

# Login to Docker Hub
echo "Logging in to Docker Hub..."
docker login -u ${DOCKER_USERNAME}

# Push backend image
echo "Pushing backend image..."
docker push ${DOCKER_USERNAME}/project-management-backend:${VERSION}
docker push ${DOCKER_USERNAME}/project-management-backend:latest

# Push frontend image
echo "Pushing frontend image..."
docker push ${DOCKER_USERNAME}/project-management-frontend:${VERSION}
docker push ${DOCKER_USERNAME}/project-management-frontend:latest

echo ""
echo "=========================================="
echo "Images pushed successfully!"
echo "=========================================="
echo "Backend: ${DOCKER_USERNAME}/project-management-backend:${VERSION}"
echo "Frontend: ${DOCKER_USERNAME}/project-management-frontend:${VERSION}"
echo ""
echo "You can now use these images in Kubernetes or docker-compose"
echo "=========================================="
