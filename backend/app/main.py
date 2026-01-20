from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio
from datetime import datetime

from app import crud, models, schemas
from app.database import SessionLocal, engine, get_db

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Direct frontend dev server
        "http://localhost:5173",  # Vite default port
        "http://localhost",        # Through nginx
        "http://localhost:80",     # Through nginx (explicit)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or handle client messages if needed
            await websocket.send_json({"type": "pong", "message": "connected"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# SSE endpoint
@app.get("/events/stream")
async def event_stream():
    async def event_generator():
        while True:
            # In a real implementation, you'd check for new events from a queue
            # For now, we'll send a heartbeat
            yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            await asyncio.sleep(30)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Helper function to broadcast project updates
async def broadcast_project_update(project_id: int, event_type: str, data: dict):
    message = {
        "type": "project_update",
        "project_id": project_id,
        "event_type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(message)

@app.get("/api/health")
def health_check():
    """Health check endpoint for CI/CD pipeline"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# User endpoints
@app.post("/api/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/api/users", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/api/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Tag endpoints
@app.get("/api/tags", response_model=List[schemas.TagResponse])
def read_tags(db: Session = Depends(get_db)):
    return crud.get_tags(db)

# Project endpoints
@app.post("/api/projects", response_model=schemas.ProjectResponse)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = crud.create_project(db=db, project=project)
    await broadcast_project_update(db_project.id, "created", {"id": db_project.id, "title": db_project.title})
    return db_project

@app.get("/api/projects", response_model=schemas.ProjectListResponse)
def read_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("updated_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    status: Optional[schemas.ProjectStatus] = None,
    owner_id: Optional[int] = None,
    tag_name: Optional[str] = None,
    health: Optional[schemas.ProjectHealth] = None,
    search_query: Optional[str] = None,
    include_deleted: bool = False,
    only_deleted: bool = False,
    db: Session = Depends(get_db)
):
    filter_params = schemas.ProjectFilter(
        status=status,
        owner_id=owner_id,
        tag_name=tag_name,
        health=health,
        search_query=search_query,
        include_deleted=include_deleted,
        only_deleted=only_deleted
    )
    skip = (page - 1) * page_size
    items, total = crud.get_projects(
        db=db,
        filter_params=filter_params,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )

    total_pages = (total + page_size - 1) // page_size

    # Convert projects to response models with proper tag serialization
    project_responses = []
    for project in items:
        project_dict = {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "short_description": project.short_description,
            "owner_id": project.owner_id,
            "status": project.status,
            "health": project.health,
            "progress": project.progress,
            "version": project.version,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "deleted_at": project.deleted_at,
            "owner": schemas.UserResponse.model_validate(project.owner) if project.owner else None,
            "tags": [schemas.TagResponse.model_validate(pt.tag) for pt in project.tags],
        }
        project_responses.append(schemas.ProjectResponse.model_validate(project_dict))

    return schemas.ProjectListResponse(
        items=project_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@app.get("/api/projects/{project_id}", response_model=schemas.ProjectDetailResponse)
def read_project(project_id: int, include_deleted: bool = False, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id, include_deleted=include_deleted)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get related data
    milestones = db.query(models.Milestone).filter(models.Milestone.project_id == project_id).all()
    team_members = db.query(models.TeamMember).filter(models.TeamMember.project_id == project_id).all()
    events = db.query(models.ProjectEvent).filter(
        models.ProjectEvent.project_id == project_id
    ).order_by(models.ProjectEvent.created_at.desc()).limit(10).all()

    # Build response using Pydantic models
    project_detail = schemas.ProjectDetailResponse(
        id=db_project.id,
        title=db_project.title,
        description=db_project.description,
        short_description=db_project.short_description,
        owner_id=db_project.owner_id,
        status=db_project.status,
        health=db_project.health,
        progress=db_project.progress,
        version=db_project.version,
        created_at=db_project.created_at,
        updated_at=db_project.updated_at,
        deleted_at=db_project.deleted_at,
        owner=schemas.UserResponse.model_validate(db_project.owner) if db_project.owner else None,
        tags=[schemas.TagResponse.model_validate(pt.tag) for pt in db_project.tags],
        milestones=[schemas.MilestoneResponse.model_validate(m) for m in milestones],
        team_members=[schemas.TeamMemberResponse(
            id=tm.id,
            project_id=tm.project_id,
            user_id=tm.user_id,
            role=tm.role,
            capacity=tm.capacity,
            created_at=tm.created_at,
            user=schemas.UserResponse.model_validate(tm.user) if tm.user else None
        ) for tm in team_members],
        recent_events=[schemas.ProjectEventResponse.model_validate(e) for e in events]
    )

    return project_detail

@app.put("/api/projects/{project_id}", response_model=schemas.ProjectResponse)
async def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):
    try:
        db_project = crud.update_project(db=db, project_id=project_id, project_update=project_update)
        if db_project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        await broadcast_project_update(project_id, "updated", {"id": project_id})

        # Convert to response model with proper tag serialization
        project_dict = {
            "id": db_project.id,
            "title": db_project.title,
            "description": db_project.description,
            "short_description": db_project.short_description,
            "owner_id": db_project.owner_id,
            "status": db_project.status,
            "health": db_project.health,
            "progress": db_project.progress,
            "version": db_project.version,
            "created_at": db_project.created_at,
            "updated_at": db_project.updated_at,
            "owner": schemas.UserResponse.model_validate(db_project.owner) if db_project.owner else None,
            "tags": [schemas.TagResponse.model_validate(pt.tag) for pt in db_project.tags],
        }
        return schemas.ProjectResponse.model_validate(project_dict)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.delete_project(db=db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await broadcast_project_update(project_id, "deleted", {"id": project_id})
    return {"message": "Project deleted"}

@app.post("/api/projects/{project_id}/recover")
async def recover_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.recover_project(db=db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    await broadcast_project_update(project_id, "recovered", {"id": project_id})
    return {"message": "Project recovered"}

# Bulk operations
@app.post("/api/projects/bulk-update", response_model=schemas.BulkUpdateResponse)
async def bulk_update_projects(
    bulk_update: schemas.BulkUpdateRequest,
    db: Session = Depends(get_db)
):
    updated_count, failed_count, errors = crud.bulk_update_projects(db=db, bulk_update=bulk_update)

    # Broadcast updates for successfully updated projects
    for project_id in bulk_update.project_ids:
        if project_id not in [int(e.split(":")[0].split()[-1]) for e in errors if "not found" not in e]:
            await broadcast_project_update(project_id, "bulk_updated", {"id": project_id})

    return schemas.BulkUpdateResponse(
        updated_count=updated_count,
        failed_count=failed_count,
        errors=errors
    )

# Milestone endpoints
@app.post("/api/projects/{project_id}/milestones", response_model=schemas.MilestoneResponse)
async def create_milestone(
    project_id: int,
    milestone: schemas.MilestoneCreate,
    db: Session = Depends(get_db)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_milestone = crud.create_milestone(db=db, milestone=milestone, project_id=project_id)
    await broadcast_project_update(project_id, "milestone_created", {"milestone_id": db_milestone.id})
    return db_milestone

@app.put("/api/milestones/{milestone_id}", response_model=schemas.MilestoneResponse)
async def update_milestone(
    milestone_id: int,
    milestone_update: schemas.MilestoneBase,
    db: Session = Depends(get_db)
):
    db_milestone = crud.update_milestone(db=db, milestone_id=milestone_id, milestone_update=milestone_update)
    if db_milestone is None:
        raise HTTPException(status_code=404, detail="Milestone not found")

    await broadcast_project_update(db_milestone.project_id, "milestone_updated", {"milestone_id": milestone_id})
    return db_milestone

# Team member endpoints
@app.post("/api/projects/{project_id}/team-members", response_model=schemas.TeamMemberResponse)
async def add_team_member(
    project_id: int,
    team_member: schemas.TeamMemberCreate,
    db: Session = Depends(get_db)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_member = crud.add_team_member(db=db, team_member=team_member, project_id=project_id)
    await broadcast_project_update(project_id, "team_member_added", {"member_id": db_member.id})
    return db_member

@app.delete("/api/team-members/{member_id}")
async def remove_team_member(member_id: int, db: Session = Depends(get_db)):
    db_member = crud.remove_team_member(db=db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Team member not found")

    await broadcast_project_update(db_member.project_id, "team_member_removed", {"member_id": member_id})
    return {"message": "Team member removed"}

@app.put("/api/team-members/{member_id}", response_model=schemas.TeamMemberResponse)
async def update_team_member(
    member_id: int,
    member_update: schemas.TeamMemberUpdate,
    db: Session = Depends(get_db)
):
    db_member = crud.update_team_member(db=db, member_id=member_id, member_update=member_update)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Team member not found")

    await broadcast_project_update(db_member.project_id, "team_member_updated", {"member_id": member_id})
    return db_member

@app.get("/")
def root():
    return {"message": "Project Management API", "version": "1.0.0"}
