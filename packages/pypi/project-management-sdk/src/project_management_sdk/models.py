"""
Pydantic models for the Project Management SDK.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectHealth(str, Enum):
    """Project health enumeration."""
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    OFF_TRACK = "off_track"


# ============================================
# User Models
# ============================================

class UserCreate(BaseModel):
    """Model for creating a new user."""
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)


class User(BaseModel):
    """User model."""
    id: int
    name: str
    email: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# Tag Models
# ============================================

class Tag(BaseModel):
    """Tag model."""
    id: int
    name: str

    class Config:
        from_attributes = True


# ============================================
# Milestone Models
# ============================================

class MilestoneCreate(BaseModel):
    """Model for creating a new milestone."""
    title: str = Field(..., min_length=1, max_length=200)
    due_date: Optional[str] = None
    completed: bool = False


class Milestone(BaseModel):
    """Milestone model."""
    id: int
    project_id: int
    title: str
    due_date: Optional[str] = None
    completed: bool = False

    class Config:
        from_attributes = True


# ============================================
# Team Member Models
# ============================================

class TeamMemberCreate(BaseModel):
    """Model for creating a new team member."""
    user_id: int
    role: str = Field(..., min_length=1, max_length=100)
    capacity: int = Field(default=100, ge=0, le=100)


class TeamMember(BaseModel):
    """Team member model."""
    id: int
    project_id: int
    user_id: int
    role: str
    capacity: int = 100
    user: Optional[User] = None

    class Config:
        from_attributes = True


# ============================================
# Project Models
# ============================================

class ProjectCreate(BaseModel):
    """Model for creating a new project."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    progress: int = Field(default=0, ge=0, le=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    owner_id: Optional[int] = None
    health: ProjectHealth = ProjectHealth.ON_TRACK
    tag_ids: List[int] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    """Model for updating an existing project."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    owner_id: Optional[int] = None
    health: Optional[ProjectHealth] = None
    tag_ids: Optional[List[int]] = None
    version: Optional[int] = None  # For optimistic concurrency


class Project(BaseModel):
    """Project model."""
    id: int
    title: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    progress: int = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    owner_id: Optional[int] = None
    health: ProjectHealth = ProjectHealth.ON_TRACK
    version: int = 1
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[Tag] = Field(default_factory=list)
    owner: Optional[User] = None

    class Config:
        from_attributes = True


class ProjectDetail(Project):
    """Extended project model with milestones and team members."""
    milestones: List[Milestone] = Field(default_factory=list)
    team_members: List[TeamMember] = Field(default_factory=list)


class ProjectListResponse(BaseModel):
    """Response model for paginated project list."""
    items: List[Project]
    total: int
    page: int
    per_page: int
    pages: int
