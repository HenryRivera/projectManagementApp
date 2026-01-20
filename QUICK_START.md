# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- OR Python 3.11+ and Node.js 18+ for local development

## Quick Start with Docker

1. **Start the application:**
   ```bash
   # On Linux/Mac
   ./start.sh
   
   # On Windows
   start.bat
   
   # Or manually (using docker compose v2)
   docker compose up -d --build
   docker compose exec backend python init_db.py
   
   # For older Docker versions, use docker-compose instead
   ```

2. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - API Documentation: http://localhost/api/docs

3. **View logs:**
   ```bash
   docker compose logs -f
   # Or: docker-compose logs -f (for older versions)
   ```

4. **Stop the application:**
   ```bash
   docker compose down
   # Or: docker-compose down (for older versions)
   ```

## Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Features Implemented

✅ **Project CRUD Operations**
- Create, read, update, and soft delete projects
- Recover deleted projects

✅ **Project Listing**
- Paginated project cards
- Sortable by title, updated date, progress
- Filterable by status, owner, tag, health
- Search across titles, descriptions, and tags

✅ **Project Detail View**
- Summary with all project information
- Milestones with progress tracking (derived percentage)
- Team roster with roles and capacity
- Recent activity events

✅ **Real-Time Updates**
- WebSocket support for live updates
- SSE (Server-Sent Events) endpoint

✅ **Bulk Operations**
- Update status or tags across multiple projects
- Optimistic concurrency control (version/ETag)

✅ **Deployment**
- Nginx reverse proxy configuration
- Docker containerization
- Production-ready setup

## API Endpoints

- `GET /api/projects` - List projects (paginated, sortable, filterable)
- `GET /api/projects/{id}` - Get project details
- `POST /api/projects` - Create project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Soft delete project
- `POST /api/projects/{id}/recover` - Recover deleted project
- `POST /api/projects/bulk-update` - Bulk update projects
- `WebSocket /ws` - Real-time updates
- `GET /events/stream` - SSE stream

## Troubleshooting

**Port already in use:**
- Change ports in `docker-compose.yml` or stop conflicting services

**Database errors:**
- Remove volumes: `docker compose down -v` (or `docker-compose down -v` for older versions)
- Reinitialize: `docker compose exec backend python init_db.py` (or `docker-compose exec backend python init_db.py`)

**Frontend not connecting to backend:**
- Check that backend is running on port 8000
- Verify CORS settings in `backend/app/main.py`
- Check browser console for errors
