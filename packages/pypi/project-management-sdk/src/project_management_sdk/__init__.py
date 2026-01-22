"""
Project Management SDK

A Python SDK for project management with Pydantic models and API client.
"""

from .models import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectStatus,
    Milestone,
    MilestoneCreate,
    TeamMember,
    TeamMemberCreate,
    User,
    UserCreate,
    Tag,
)

from .client import ProjectManagementClient

__version__ = "1.0.0"

__all__ = [
    # Models
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectStatus",
    "Milestone",
    "MilestoneCreate",
    "TeamMember",
    "TeamMemberCreate",
    "User",
    "UserCreate",
    "Tag",
    # Client
    "ProjectManagementClient",
]
