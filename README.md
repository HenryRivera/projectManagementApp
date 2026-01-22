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
| **Deployment** | Docker, Docker Compose, Nginx |
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
├── scripts/                 # Build & deploy scripts
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
| GET | `/api/users/{id}` | Get user by ID |
| POST | `/api/users` | Create user |
| GET | `/api/tags` | List tags |

### Real-Time & Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api` | API info and available endpoints |
| GET | `/api/health` | Health check |
| WebSocket | `/ws` | Real-time updates |
| GET | `/events/stream` | SSE stream |

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
| `DATABASE_URL` | `sqlite:///./data/projects.db` | Database connection string |

---

## Scripts

| Script | Description |
|--------|-------------|
| `./start.sh` | Start the application (and Jenkins if installed) |
| `./stop.sh` | Stop the application (and Jenkins if running) |
| `./scripts/build-and-push.sh` | Build & push Docker images to Docker Hub |
| `./scripts/publish-npm.sh` | Build & publish NPM package |
| `./scripts/publish-pypi.sh` | Build & publish PyPI package |

---

## Publishable Packages

This project includes reusable packages that can be published to NPM and PyPI.

### NPM Package: `@henryrivera/project-management-ui`

A React component library for project management interfaces.

#### Installation

```bash
npm install @henryrivera/project-management-ui
```

#### Components

##### ProjectCard

Displays a project summary card with progress indicator.

```tsx
import { ProjectCard } from '@henryrivera/project-management-ui';

<ProjectCard
  id={1}
  name="Website Redesign"
  description="Complete overhaul of company website"
  status="In Progress"
  progress={65}
  onClick={(id) => console.log('Clicked project:', id)}
/>
```

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `id` | `number` | ✅ | Project unique identifier |
| `name` | `string` | ✅ | Project name |
| `description` | `string` | ❌ | Project description |
| `status` | `string` | ✅ | Current status |
| `progress` | `number` | ❌ | Progress percentage (0-100) |
| `onClick` | `(id: number) => void` | ❌ | Click handler |

##### ProgressBar

A customizable progress bar component.

```tsx
import { ProgressBar } from '@henryrivera/project-management-ui';

<ProgressBar value={75} max={100} showLabel height={8} />
```

**Props:**

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `value` | `number` | ✅ | - | Current value |
| `max` | `number` | ❌ | `100` | Maximum value |
| `showLabel` | `boolean` | ❌ | `false` | Show percentage label |
| `height` | `number` | ❌ | `8` | Height in pixels |
| `color` | `string` | ❌ | - | Custom bar color |
| `backgroundColor` | `string` | ❌ | - | Custom background color |

#### Publishing to NPM

```bash
cd packages/npm/project-management-ui
npm login
npm run build
npm publish --access public
```

---

### PyPI Package: `project-management-sdk`

A Python SDK for interacting with the Project Management API.

#### Installation

```bash
pip install project-management-sdk
```

#### Quick Start

```python
from project_management_sdk import ProjectManagementClient, ProjectCreate

# Initialize client
client = ProjectManagementClient(base_url="http://localhost/api")

# Create a project
new_project = ProjectCreate(
    name="Website Redesign",
    description="Complete overhaul of company website",
    status="Planning"
)
project = client.create_project(new_project)
print(f"Created project: {project.name} (ID: {project.id})")

# List all projects
projects = client.get_projects()
for p in projects:
    print(f"- {p.name}: {p.status}")

# Update a project
from project_management_sdk import ProjectUpdate
updated = client.update_project(project.id, ProjectUpdate(status="In Progress", progress=25))

# Delete a project
client.delete_project(project.id)
```

#### Models

##### Project

```python
class Project(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    progress: int
    priority: str
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    version: int
    is_deleted: bool
    milestones: List[Milestone]
    team_members: List[TeamMember]
    tags: List[Tag]
```

##### ProjectCreate / ProjectUpdate

```python
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    status: str = "Planning"
    progress: int = 0
    priority: str = "Medium"
    start_date: Optional[date]
    end_date: Optional[date]

class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    status: Optional[str]
    progress: Optional[int]
    priority: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    version: Optional[int]  # For optimistic concurrency
```

#### API Methods

| Method | Description |
|--------|-------------|
| `get_projects(skip, limit)` | List projects with pagination |
| `get_project(id)` | Get a single project by ID |
| `create_project(project)` | Create a new project |
| `update_project(id, project)` | Update an existing project |
| `delete_project(id)` | Soft delete a project |
| `health_check()` | Check API health status |

#### Async Support

```python
import asyncio
from project_management_sdk import AsyncProjectManagementClient

async def main():
    async with AsyncProjectManagementClient(base_url="http://localhost/api") as client:
        projects = await client.get_projects()
        for p in projects:
            print(f"- {p.name}")

asyncio.run(main())
```

#### Publishing to PyPI

```bash
cd packages/pypi/project-management-sdk
pip install build twine
python -m build
twine upload dist/*
```

---

## License

MIT
