# Containerized Deployment Guide

This guide covers deploying the Project Management application using Docker and Kubernetes.

## Table of Contents

1. [Docker Hub Image Deployment](#docker-hub-image-deployment)
2. [Kubernetes Deployment](#kubernetes-deployment)
3. [Alternative Container Registries](#alternative-container-registries)
4. [Troubleshooting](#troubleshooting)

## Docker Hub Image Deployment

### Prerequisites

- Docker installed and running
- Docker Hub account (or alternative registry)
- kubectl installed (for Kubernetes deployment)

### Step 1: Build and Push Images

#### Option A: Using the provided script (Recommended)

**Linux/Mac:**
```bash
./scripts/build-and-push.sh your-dockerhub-username v1.0.0
```

**Windows:**
```cmd
scripts\build-and-push.bat your-dockerhub-username v1.0.0
```

#### Option B: Manual build and push

```bash
# Set your Docker Hub username
export DOCKER_USERNAME=your-dockerhub-username
export VERSION=v1.0.0

# Build backend image
docker build -f backend/Dockerfile.prod -t ${DOCKER_USERNAME}/project-management-backend:${VERSION} ./backend
docker tag ${DOCKER_USERNAME}/project-management-backend:${VERSION} ${DOCKER_USERNAME}/project-management-backend:latest

# Build frontend image
docker build -f frontend/Dockerfile.prod -t ${DOCKER_USERNAME}/project-management-frontend:${VERSION} ./frontend
docker tag ${DOCKER_USERNAME}/project-management-frontend:${VERSION} ${DOCKER_USERNAME}/project-management-frontend:latest

# Login to Docker Hub
docker login -u ${DOCKER_USERNAME}

# Push images
docker push ${DOCKER_USERNAME}/project-management-backend:${VERSION}
docker push ${DOCKER_USERNAME}/project-management-backend:latest
docker push ${DOCKER_USERNAME}/project-management-frontend:${VERSION}
docker push ${DOCKER_USERNAME}/project-management-frontend:latest
```

### Step 2: Verify Images

Check that your images are available:
```bash
docker images | grep project-management
```

Or visit: `https://hub.docker.com/r/your-username/project-management-backend`

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (local with minikube/kind, or cloud provider)
- kubectl configured to access your cluster
- Ingress controller installed (nginx-ingress recommended)

### Step 1: Update Image Names

Edit the Kubernetes deployment files to use your Docker Hub images:

```bash
# Replace YOUR_DOCKERHUB_USERNAME in deployment files
sed -i 's/YOUR_DOCKERHUB_USERNAME/your-actual-username/g' k8s/backend-deployment.yaml
sed -i 's/YOUR_DOCKERHUB_USERNAME/your-actual-username/g' k8s/frontend-deployment.yaml
```

Or use the provided deployment script:
```bash
./k8s/deploy.sh your-dockerhub-username
```

### Step 2: Deploy to Kubernetes

#### Option A: Using the deployment script

```bash
./k8s/deploy.sh your-dockerhub-username
```

#### Option B: Manual deployment

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create config map
kubectl apply -f k8s/configmap.yaml

# Create persistent volume
kubectl apply -f k8s/persistent-volume.yaml

# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Create ingress
kubectl apply -f k8s/ingress.yaml

# Initialize database
kubectl run init-db --image=your-username/project-management-backend:latest \
  --restart=Never -n project-management -- python init_db.py
```

#### Option C: Using Kustomize

```bash
kubectl apply -k k8s/
```

### Step 3: Verify Deployment

```bash
# Check pods
kubectl get pods -n project-management

# Check services
kubectl get services -n project-management

# Check ingress
kubectl get ingress -n project-management

# View logs
kubectl logs -f deployment/backend -n project-management
kubectl logs -f deployment/frontend -n project-management
```

### Step 4: Access the Application

#### Local Development (minikube/kind)

```bash
# Get ingress IP
kubectl get ingress -n project-management

# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
# <ingress-ip> project-management.local
```

Then access: `http://project-management.local`

#### Cloud Provider

Update the ingress hostname in `k8s/ingress.yaml` to your domain, then access via your domain.

### Configuration

#### Environment Variables

Edit `k8s/configmap.yaml` to change configuration:

```yaml
data:
  DATABASE_URL: "postgresql://user:password@postgres-service:5432/projects"
```

#### Resource Limits

Adjust CPU and memory limits in:
- `k8s/backend-deployment.yaml`
- `k8s/frontend-deployment.yaml`

#### Scaling

Scale deployments:

```bash
kubectl scale deployment backend --replicas=3 -n project-management
kubectl scale deployment frontend --replicas=3 -n project-management
```

## Alternative Container Registries

### Google Container Registry (GCR)

```bash
# Tag images
docker tag project-management-backend:latest gcr.io/PROJECT_ID/project-management-backend:latest
docker tag project-management-frontend:latest gcr.io/PROJECT_ID/project-management-frontend:latest

# Push
docker push gcr.io/PROJECT_ID/project-management-backend:latest
docker push gcr.io/PROJECT_ID/project-management-frontend:latest
```

### Amazon ECR

```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create repositories (first time)
aws ecr create-repository --repository-name project-management-backend
aws ecr create-repository --repository-name project-management-frontend

# Tag and push
docker tag project-management-backend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/project-management-backend:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/project-management-backend:latest
```

### Azure Container Registry (ACR)

```bash
# Login
az acr login --name YOUR_REGISTRY_NAME

# Tag and push
docker tag project-management-backend:latest YOUR_REGISTRY_NAME.azurecr.io/project-management-backend:latest
docker push YOUR_REGISTRY_NAME.azurecr.io/project-management-backend:latest
```

### GitHub Container Registry (GHCR)

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag and push
docker tag project-management-backend:latest ghcr.io/USERNAME/project-management-backend:latest
docker push ghcr.io/USERNAME/project-management-backend:latest
```

## Docker Compose with Registry Images

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: your-username/project-management-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/projects.db
    volumes:
      - backend-data:/app/data

  frontend:
    image: your-username/project-management-frontend:latest
    ports:
      - "80:80"

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend

volumes:
  backend-data:
```

Deploy:
```bash
docker compose -f docker-compose.prod.yml up -d
```

**Note:** Modern Docker installations use `docker compose` (v2). If you're using an older version, you may need to use `docker-compose` instead.

## Troubleshooting

### Images Not Found

**Error:** `ImagePullBackOff` or `ErrImagePull`

**Solution:**
1. Verify image exists: `docker pull your-username/project-management-backend:latest`
2. Check image name in deployment files
3. Ensure you're logged in: `docker login`
4. For private registries, create image pull secrets:
   ```bash
   kubectl create secret docker-registry regcred \
     --docker-server=https://index.docker.io/v1/ \
     --docker-username=your-username \
     --docker-password=your-password \
     --docker-email=your-email \
     -n project-management
   ```
   Then add to deployment:
   ```yaml
   spec:
     imagePullSecrets:
     - name: regcred
   ```

### Pods Not Starting

**Check logs:**
```bash
kubectl describe pod <pod-name> -n project-management
kubectl logs <pod-name> -n project-management
```

**Common issues:**
- Resource limits too low
- Database connection issues
- Missing environment variables

### Ingress Not Working

**Check ingress controller:**
```bash
kubectl get pods -n ingress-nginx
```

**Verify ingress:**
```bash
kubectl describe ingress project-management-ingress -n project-management
```

### Database Initialization

If database initialization fails:
```bash
# Run init script manually
kubectl exec -it deployment/backend -n project-management -- python init_db.py
```

## Production Considerations

1. **Use PostgreSQL** instead of SQLite for production
2. **Enable SSL/TLS** in ingress configuration
3. **Set up monitoring** (Prometheus, Grafana)
4. **Configure resource limits** appropriately
5. **Set up backups** for persistent volumes
6. **Use secrets** for sensitive data (database passwords, API keys)
7. **Enable horizontal pod autoscaling** (HPA)
8. **Set up CI/CD** pipeline for automated deployments

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v2
        with:
          context: ./backend
          file: ./backend/Dockerfile.prod
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/project-management-backend:${{ github.ref_name }}
      
      - name: Build and push frontend
        uses: docker/build-push-action@v2
        with:
          context: ./frontend
          file: ./frontend/Dockerfile.prod
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/project-management-frontend:${{ github.ref_name }}
```
