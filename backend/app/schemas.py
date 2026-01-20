from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import ProjectStatus, ProjectHealth, UserRole

# User Schemas
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# Tag Schemas
class TagBase(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True

# Milestone Schemas
class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneResponse(MilestoneBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Team Member Schemas
class TeamMemberBase(BaseModel):
    user_id: int
    role: UserRole
    capacity: float = Field(ge=0.0, le=1.0)

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberUpdate(BaseModel):
    role: Optional[UserRole] = None
    capacity: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class TeamMemberResponse(TeamMemberBase):
    id: int
    project_id: int
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

# Project Event Schemas
class ProjectEventResponse(BaseModel):
    id: int
    project_id: int
    event_type: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True

# Project Schemas
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    owner_id: Optional[int] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    health: ProjectHealth = ProjectHealth.HEALTHY

class ProjectCreate(ProjectBase):
    tag_names: Optional[List[str]] = []

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    owner_id: Optional[int] = None
    status: Optional[ProjectStatus] = None
    health: Optional[ProjectHealth] = None
    tag_names: Optional[List[str]] = None
    version: Optional[int] = None  # For optimistic concurrency

class ProjectResponse(ProjectBase):
    id: int
    progress: float
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    owner: Optional[UserResponse] = None
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True

class ProjectDetailResponse(ProjectResponse):
    milestones: List[MilestoneResponse] = []
    team_members: List[TeamMemberResponse] = []
    recent_events: List[ProjectEventResponse] = []

# Bulk Operations
class BulkUpdateRequest(BaseModel):
    project_ids: List[int]
    status: Optional[ProjectStatus] = None
    tag_names: Optional[List[str]] = None
    version: Optional[int] = None  # Expected version for optimistic concurrency

class BulkUpdateResponse(BaseModel):
    updated_count: int
    failed_count: int
    errors: List[str] = []

# Search and Filter
class ProjectFilter(BaseModel):
    status: Optional[ProjectStatus] = None
    owner_id: Optional[int] = None
    tag_name: Optional[str] = None
    health: Optional[ProjectHealth] = None
    search_query: Optional[str] = None
    include_deleted: bool = False
    only_deleted: bool = False

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
