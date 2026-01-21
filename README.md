# Project Management System

A full-stack project management application with real-time updates, CI/CD pipeline, and containerized deployment.

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone the Repository

```bash
git clone https://github.com/HenryRivera/projectManagementApp.git
cd projectManagementApp
```

### 2. Start the Application

```bash
./start.sh
```

### 3. Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost |
| **API Docs** | http://localhost/api/docs |
| **API Health** | http://localhost/api/health |
| **Jenkins** | http://localhost:8081 (if installed) |

### 4. Stop the Application

```bash
./stop.sh
```

---

## Features

- **Project CRUD Operations**: Create, read, update, and soft delete projects
- **Paginated Listing**: Projects displayed as cards (9 per page)
- **Sorting & Filtering**: Sort by title, updated date, progress. Filter by status, owner, tag, health
- **Search**: Free-text search across titles, descriptions, and tags
- **Project Detail View**:
  - Summary with expandable description
  - Milestones with progress tracking
  - Team roster with editable capacity
  - Recent activity events
- **Real-Time Updates**: WebSocket support for live updates
- **Bulk Operations**: Update multiple projects with optimistic concurrency control
- **Soft Delete with Recovery**: Deleted projects can be recovered
- **SSO Login**: Demo authentication flow

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, React Router, Vite, Axios |
| **Backend** | FastAPI, SQLAlchemy, Pydantic |
| **Database** | SQLite (PostgreSQL ready) |
| **Real-Time** | WebSockets, Server-Sent Events |
| **Deployment** | Docker, Nginx, Kubernetes |
| **CI/CD** | GitHub Actions, Jenkins |

---

## Project Structure

```
projectManagementApp/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # API endpoints
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   └── crud.py         # Database operations
│   ├── tests/              # Pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── api/            # API client
│   │   └── App.jsx
│   ├── Dockerfile
│   └── package.json
├── nginx/                   # Reverse proxy config
│   └── default.conf
├── k8s/                     # Kubernetes manifests
├── .github/workflows/       # GitHub Actions CI
├── docker-compose.yml
├── Jenkinsfile             # Jenkins pipeline
├── start.sh                # Start script
└── stop.sh                 # Stop script
```

---

## API Endpoints

### Projects
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List projects (paginated, sortable, filterable) |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/{id}` | Get project details |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Soft delete project |
| POST | `/api/projects/{id}/recover` | Recover deleted project |
| POST | `/api/projects/bulk-update` | Bulk update projects |

### Milestones
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{id}/milestones` | Add milestone |
| PUT | `/api/milestones/{id}` | Update milestone |
| DELETE | `/api/milestones/{id}` | Delete milestone |

### Team Members
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/{id}/team-members` | Add team member |
| PUT | `/api/team-members/{id}` | Update team member |
| DELETE | `/api/team-members/{id}` | Remove team member |

### Users & Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List users |
| POST | `/api/users` | Create user |
| GET | `/api/tags` | List tags |

### Real-Time & Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| WebSocket | `/ws` | Real-time updates |
| GET | `/events/stream` | SSE stream |
| GET | `/api/health` | Health check |

---

## Local Development (Without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## CI/CD Pipeline

### GitHub Actions (Automated Testing)

Every push to GitHub triggers:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Lint Python │     │ Lint JS     │     │ Test DB     │
│   (ruff)    │     │  (eslint)   │     │ Migrations  │
└──────┬──────┘     └──────┬──────┘     └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ Test Backend│     │Test Frontend│
│  (pytest)   │     │  (vitest)   │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 ▼
       ┌─────────────────┐
       │Integration Tests│
       │   (Docker)      │
       └─────────────────┘
```

### Jenkins (Deployment)

Optional local CI/CD with Jenkins:

```bash
# Start Jenkins
docker run -d --name jenkins -p 8081:8080 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --user root jenkins/jenkins:lts

# Get initial password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Configure at http://localhost:8081 with Pipeline from SCM pointing to this repo.

---

## Kubernetes Deployment

### Deploy to Kubernetes

```bash
# Update with your Docker Hub username
./k8s/deploy.sh your-dockerhub-username
```

### Manual Deployment

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/persistent-volume.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### Verify Deployment

```bash
kubectl get pods -n project-management
kubectl get services -n project-management
kubectl get ingress -n project-management
```

---

## Docker Hub Deployment

### Build & Push Images

```bash
# Using the provided script
./scripts/build-and-push.sh your-dockerhub-username v1.0.0

# Or manually
docker build -f backend/Dockerfile.prod -t your-username/project-management-backend:v1.0.0 ./backend
docker build -f frontend/Dockerfile.prod -t your-username/project-management-frontend:v1.0.0 ./frontend
docker push your-username/project-management-backend:v1.0.0
docker push your-username/project-management-frontend:v1.0.0
```

---

## Running Tests

### Backend Tests

```bash
cd backend
pip install pytest pytest-cov httpx
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm install
npm test
```

---

## Troubleshooting

### Containers Won't Start

```bash
docker compose ps              # Check status
docker compose logs            # View logs
docker compose down -v         # Full reset
docker compose up -d --build   # Rebuild
```

### Port 80 Already in Use

```bash
lsof -i :80                    # Find what's using port 80
# Edit docker-compose.yml to change "80:80" to "3000:80"
```

### Database Issues

```bash
docker compose down -v                                    # Remove volumes
docker compose up -d --build                              # Rebuild
docker exec project-management-backend python init_db.py  # Reinitialize
```

### Nginx Restarting

```bash
docker logs project-management-nginx   # Check error logs
docker rm -f project-management-nginx  # Remove and recreate
docker compose up -d
```

---

## Environment Variables

### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./projects.db` | Database connection string |

### Frontend
| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_WS_URL` | `ws://localhost:8000` | WebSocket URL |

---

## Scripts

| Script | Description |
|--------|-------------|
| `./start.sh` | Start app + Jenkins |
| `./stop.sh` | Stop app + Jenkins |
| `./scripts/build-and-push.sh` | Build & push Docker images |
| `./k8s/deploy.sh` | Deploy to Kubernetes |

---

## License

MIT
