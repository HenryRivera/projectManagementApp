# Project Management System

A full-stack project management application with real-time updates, built with React and FastAPI.

## Features

- **Project CRUD Operations**: Create, read, update, and soft delete projects
- **Paginated Listing**: Projects displayed as cards with pagination
- **Sorting & Filtering**: Sort by title, updated date, progress. Filter by status, owner, tag, and health
- **Project Detail View**: 
  - Summary with project information
  - Milestones with progress tracking (derived percentage)
  - Team roster with roles and capacity
  - Recent activity events
- **Real-Time Updates**: WebSocket and SSE support for live project updates
- **Search**: Free-text search across project titles, descriptions, and tags (using SQL LIKE queries)
- **Bulk Operations**: Update status or tags across multiple projects with optimistic concurrency control (version/ETag)
- **Soft Delete with Recovery**: Projects can be soft deleted and recovered

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Database (can be switched to PostgreSQL)
- **WebSockets**: Real-time bidirectional communication
- **SSE**: Server-Sent Events for real-time updates

### Frontend
- **React 18**: UI library
- **React Router**: Client-side routing
- **Vite**: Build tool and dev server
- **Axios**: HTTP client

### Deployment
- **Nginx**: Reverse proxy and load balancer
- **Docker**: Containerization

## Project Structure

```
aida_case_study/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── database.py      # Database configuration
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── crud.py          # CRUD operations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── init_db.py           # Database initialization script
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── api/             # API client functions
│   │   ├── hooks/           # Custom React hooks
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   └── nginx.conf           # Nginx configuration
├── docker-compose.yml
└── README.md
```

## Search Implementation

The search functionality uses **SQL LIKE queries** with case-insensitive matching across:
- Project titles
- Project descriptions (full and short)
- Project tags

This approach is simple and effective for small to medium datasets. For larger scale applications, consider:
- **PostgreSQL Full-Text Search**: Better performance and relevance ranking
- **Elasticsearch**: Advanced search with fuzzy matching, faceting, etc.
- **Algolia/Meilisearch**: External search engines with excellent performance

## Optimistic Concurrency Control

Bulk operations use **version numbers (ETag pattern)** to prevent concurrent modification conflicts:
- Each project has a `version` field that increments on updates
- When updating, clients must provide the expected version
- If versions don't match, the operation fails with a 409 Conflict error
- This ensures data consistency in multi-user scenarios

## Getting Started

### Prerequisites
- Docker and Docker Compose
- OR Python 3.11+ and Node.js 18+ for local development

### Using Docker (Recommended)

1. Clone the repository
2. Start all services:
   ```bash
   docker-compose up -d
   ```

3. Initialize the database with sample data:
   ```bash
   docker compose exec backend python init_db.py
   ```

4. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - API Docs: http://localhost/api/docs

### Local Development

#### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize database:
   ```bash
   python init_db.py
   ```

5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

Backend will be available at http://localhost:8000

#### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

Frontend will be available at http://localhost:3000

## API Endpoints

### Projects
- `GET /api/projects` - List projects (with pagination, sorting, filtering)
- `GET /api/projects/{id}` - Get project details
- `POST /api/projects` - Create project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Soft delete project
- `POST /api/projects/{id}/recover` - Recover deleted project
- `POST /api/projects/bulk-update` - Bulk update projects

### Milestones
- `POST /api/projects/{id}/milestones` - Create milestone
- `PUT /api/milestones/{id}` - Update milestone

### Team Members
- `POST /api/projects/{id}/team-members` - Add team member
- `DELETE /api/team-members/{id}` - Remove team member

### Real-Time
- `WebSocket /ws` - WebSocket connection for real-time updates
- `GET /events/stream` - SSE endpoint for event streaming

## Deployment

### Local Development

The application is configured for deployment with Nginx as a reverse proxy:

1. **Build and start containers**:
   ```bash
   docker compose up -d --build
   # Note: Modern Docker uses 'docker compose' (v2). Older versions use 'docker-compose'
   ```

2. **Nginx configuration** is in `nginx/nginx.conf` and handles:
   - Routing frontend requests
   - Proxying API requests to backend
   - WebSocket upgrade handling
   - SSE streaming support

### Container Registry Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on:
- Building and pushing images to Docker Hub
- Deploying to Kubernetes
- Using alternative container registries (GCR, ECR, ACR, GHCR)

**Quick Start - Push to Docker Hub:**
```bash
./scripts/build-and-push.sh your-dockerhub-username v1.0.0
```

**Quick Start - Deploy to Kubernetes:**
```bash
./k8s/deploy.sh your-dockerhub-username
```

### Production Considerations

- Use environment variables for sensitive data
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Use PostgreSQL instead of SQLite for production
- Configure proper logging and monitoring
- Use production Dockerfiles (`Dockerfile.prod`) for optimized builds

## Environment Variables

### Backend
- `DATABASE_URL`: Database connection string (default: `sqlite:///./projects.db`)

### Frontend
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)
- `VITE_WS_URL`: WebSocket URL (default: `ws://localhost:8000`)

## License

MIT
