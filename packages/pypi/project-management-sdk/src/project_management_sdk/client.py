"""
API Client for the Project Management SDK.
"""

from typing import Optional, List, Dict, Any
import httpx

from .models import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectDetail,
    ProjectListResponse,
    Milestone,
    MilestoneCreate,
    TeamMember,
    TeamMemberCreate,
    User,
    UserCreate,
    Tag,
)


class ProjectManagementClient:
    """
    HTTP client for interacting with the Project Management API.

    Usage:
        client = ProjectManagementClient(base_url="http://localhost/api")

        # List projects
        projects = client.list_projects(page=1, per_page=10)

        # Create a project
        project = client.create_project(ProjectCreate(title="New Project"))

        # Get project details
        project = client.get_project(project_id=1)
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Initialize the client.

        Args:
            base_url: The base URL of the API (e.g., "http://localhost/api")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "ProjectManagementClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    # ============================================
    # Health
    # ============================================

    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = self._client.get("/health")
        response.raise_for_status()
        return response.json()

    # ============================================
    # Projects
    # ============================================

    def list_projects(
        self,
        page: int = 1,
        per_page: int = 9,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
        status: Optional[str] = None,
        owner_id: Optional[int] = None,
        tag: Optional[str] = None,
        health: Optional[str] = None,
        search: Optional[str] = None,
        include_deleted: bool = False,
    ) -> ProjectListResponse:
        """
        List projects with pagination and filtering.

        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            status: Filter by status
            owner_id: Filter by owner ID
            tag: Filter by tag name
            health: Filter by health status
            search: Search query
            include_deleted: Include soft-deleted projects

        Returns:
            ProjectListResponse with paginated projects
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "include_deleted": include_deleted,
        }
        if status:
            params["status"] = status
        if owner_id:
            params["owner_id"] = owner_id
        if tag:
            params["tag"] = tag
        if health:
            params["health"] = health
        if search:
            params["search"] = search

        response = self._client.get("/projects", params=params)
        response.raise_for_status()
        return ProjectListResponse(**response.json())

    def get_project(self, project_id: int) -> ProjectDetail:
        """
        Get project details by ID.

        Args:
            project_id: The project ID

        Returns:
            ProjectDetail with full project information
        """
        response = self._client.get(f"/projects/{project_id}")
        response.raise_for_status()
        return ProjectDetail(**response.json())

    def create_project(self, project: ProjectCreate) -> Project:
        """
        Create a new project.

        Args:
            project: Project data

        Returns:
            Created project
        """
        response = self._client.post("/projects", json=project.model_dump())
        response.raise_for_status()
        return Project(**response.json())

    def update_project(self, project_id: int, project: ProjectUpdate) -> Project:
        """
        Update an existing project.

        Args:
            project_id: The project ID
            project: Updated project data

        Returns:
            Updated project
        """
        response = self._client.put(
            f"/projects/{project_id}",
            json=project.model_dump(exclude_none=True)
        )
        response.raise_for_status()
        return Project(**response.json())

    def delete_project(self, project_id: int) -> Dict[str, str]:
        """
        Soft delete a project.

        Args:
            project_id: The project ID

        Returns:
            Confirmation message
        """
        response = self._client.delete(f"/projects/{project_id}")
        response.raise_for_status()
        return response.json()

    def recover_project(self, project_id: int) -> Dict[str, str]:
        """
        Recover a soft-deleted project.

        Args:
            project_id: The project ID

        Returns:
            Confirmation message
        """
        response = self._client.post(f"/projects/{project_id}/recover")
        response.raise_for_status()
        return response.json()

    # ============================================
    # Milestones
    # ============================================

    def add_milestone(self, project_id: int, milestone: MilestoneCreate) -> Milestone:
        """
        Add a milestone to a project.

        Args:
            project_id: The project ID
            milestone: Milestone data

        Returns:
            Created milestone
        """
        response = self._client.post(
            f"/projects/{project_id}/milestones",
            json=milestone.model_dump()
        )
        response.raise_for_status()
        return Milestone(**response.json())

    def update_milestone(self, milestone_id: int, data: Dict[str, Any]) -> Milestone:
        """
        Update a milestone.

        Args:
            milestone_id: The milestone ID
            data: Updated data

        Returns:
            Updated milestone
        """
        response = self._client.put(f"/milestones/{milestone_id}", json=data)
        response.raise_for_status()
        return Milestone(**response.json())

    # ============================================
    # Team Members
    # ============================================

    def add_team_member(self, project_id: int, member: TeamMemberCreate) -> TeamMember:
        """
        Add a team member to a project.

        Args:
            project_id: The project ID
            member: Team member data

        Returns:
            Created team member
        """
        response = self._client.post(
            f"/projects/{project_id}/team-members",
            json=member.model_dump()
        )
        response.raise_for_status()
        return TeamMember(**response.json())

    def update_team_member(self, member_id: int, data: Dict[str, Any]) -> TeamMember:
        """
        Update a team member.

        Args:
            member_id: The team member ID
            data: Updated data

        Returns:
            Updated team member
        """
        response = self._client.put(f"/team-members/{member_id}", json=data)
        response.raise_for_status()
        return TeamMember(**response.json())

    def remove_team_member(self, member_id: int) -> Dict[str, str]:
        """
        Remove a team member.

        Args:
            member_id: The team member ID

        Returns:
            Confirmation message
        """
        response = self._client.delete(f"/team-members/{member_id}")
        response.raise_for_status()
        return response.json()

    # ============================================
    # Users
    # ============================================

    def list_users(self) -> List[User]:
        """List all users."""
        response = self._client.get("/users")
        response.raise_for_status()
        return [User(**u) for u in response.json()]

    def create_user(self, user: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user: User data

        Returns:
            Created user
        """
        response = self._client.post("/users", json=user.model_dump())
        response.raise_for_status()
        return User(**response.json())

    def get_user(self, user_id: int) -> User:
        """
        Get user by ID.

        Args:
            user_id: The user ID

        Returns:
            User
        """
        response = self._client.get(f"/users/{user_id}")
        response.raise_for_status()
        return User(**response.json())

    # ============================================
    # Tags
    # ============================================

    def list_tags(self) -> List[Tag]:
        """List all tags."""
        response = self._client.get("/tags")
        response.raise_for_status()
        return [Tag(**t) for t in response.json()]
