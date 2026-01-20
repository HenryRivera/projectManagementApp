from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base
import uuid

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectHealth(str, enum.Enum):
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    CRITICAL = "critical"

class UserRole(str, enum.Enum):
    OWNER = "owner"
    MANAGER = "manager"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    QA = "qa"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    short_description = Column(String(500))
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING, index=True)
    health = Column(SQLEnum(ProjectHealth), default=ProjectHealth.HEALTHY, index=True)
    progress = Column(Float, default=0.0)  # Derived from milestones
    version = Column(Integer, default=1)  # For optimistic concurrency
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    owner = relationship("User", back_populates="owned_projects")
    tags = relationship("ProjectTag", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    team_members = relationship("TeamMember", back_populates="project", cascade="all, delete-orphan")
    events = relationship("ProjectEvent", back_populates="project", cascade="all, delete-orphan", order_by="ProjectEvent.created_at.desc()")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    
    owned_projects = relationship("Project", back_populates="owner")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    
    projects = relationship("ProjectTag", back_populates="tag")

class ProjectTag(Base):
    __tablename__ = "project_tags"
    
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    
    project = relationship("Project", back_populates="tags")
    tag = relationship("Tag", back_populates="projects")

class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    completed = Column(Boolean, default=False)
    due_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    project = relationship("Project", back_populates="milestones")

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    capacity = Column(Float, default=1.0)  # 0.0 to 1.0 (full-time)
    created_at = Column(DateTime, server_default=func.now())
    
    project = relationship("Project", back_populates="team_members")
    user = relationship("User")

class ProjectEvent(Base):
    __tablename__ = "project_events"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # e.g., "milestone_completed", "status_changed", "team_member_added"
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    project = relationship("Project", back_populates="events")
