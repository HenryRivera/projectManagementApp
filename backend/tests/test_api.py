import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Create in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


# ============================================
# Health Check Tests
# ============================================
class TestHealthCheck:
    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


# ============================================
# Project Tests
# ============================================
class TestProjects:
    def test_list_projects_empty(self, client):
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"] == []
        assert data["total"] == 0

    def test_create_project(self, client):
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Project"
        assert data["id"] is not None

    def test_get_project(self, client):
        # Create a project first
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        # Get the project
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test Project"

    def test_get_project_not_found(self, client):
        response = client.get("/api/projects/99999")
        assert response.status_code == 404

    def test_update_project(self, client):
        # Create a project first
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        # Update the project
        update_data = {"title": "Updated Project"}
        response = client.put(f"/api/projects/{project_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Project"

    def test_delete_project(self, client):
        # Create a project first
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        # Delete the project
        response = client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 200

        # Verify it's deleted (soft delete - should not appear in list)
        list_response = client.get("/api/projects")
        assert list_response.json()["total"] == 0

    def test_recover_project(self, client):
        # Create a project first
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        # Delete the project
        client.delete(f"/api/projects/{project_id}")

        # Recover the project
        response = client.post(f"/api/projects/{project_id}/recover")
        assert response.status_code == 200

        # Verify it's recovered
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 200

    def test_project_pagination(self, client):
        # Get initial count
        initial_response = client.get("/api/projects?skip=0&limit=1")
        initial_total = initial_response.json()["total"]

        # Create multiple projects
        for i in range(15):
            project_data = {
                "title": f"Project {i}",
                "description": "A test project",
                "status": "active",
                "health": "healthy"
            }
            client.post("/api/projects", json=project_data)

        # Get first page
        response = client.get("/api/projects?skip=0&limit=10")
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == initial_total + 15


# ============================================
# User Tests
# ============================================
class TestUsers:
    def test_list_users(self, client):
        response = client.get("/api/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_user(self, client):
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "Developer"
        }
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Test User"


# ============================================
# Tag Tests
# ============================================
class TestTags:
    def test_list_tags(self, client):
        response = client.get("/api/tags")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ============================================
# Milestone Tests
# ============================================
class TestMilestones:
    def test_create_milestone(self, client):
        # Create a project first
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        project_response = client.post("/api/projects", json=project_data)
        project_id = project_response.json()["id"]

        # Create a milestone
        milestone_data = {
            "title": "Milestone 1",
            "due_date": "2026-02-01T00:00:00"
        }
        response = client.post(f"/api/projects/{project_id}/milestones", json=milestone_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Milestone 1"

    def test_update_milestone(self, client):
        # Create a project first
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        project_response = client.post("/api/projects", json=project_data)
        project_id = project_response.json()["id"]

        # Create a milestone
        milestone_data = {
            "title": "Milestone 1",
            "due_date": "2026-02-01T00:00:00"
        }
        milestone_response = client.post(f"/api/projects/{project_id}/milestones", json=milestone_data)
        milestone_id = milestone_response.json()["id"]

        # Update the milestone
        update_data = {"title": "Updated Milestone", "completed": True}
        response = client.put(f"/api/milestones/{milestone_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Milestone"


# ============================================
# Team Member Tests
# ============================================
class TestTeamMembers:
    def test_add_team_member(self, client):
        # Create a project first
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        project_response = client.post("/api/projects", json=project_data)
        project_id = project_response.json()["id"]

        # Create a user
        user_data = {"name": "John Doe", "email": "john@example.com"}
        user_response = client.post("/api/users", json=user_data)
        user_id = user_response.json()["id"]

        # Add team member
        team_member_data = {
            "user_id": user_id,
            "role": "developer",
            "capacity": 1.0
        }
        response = client.post(f"/api/projects/{project_id}/team-members", json=team_member_data)
        assert response.status_code == 200
        assert response.json()["role"] == "developer"

    def test_update_team_member_capacity(self, client):
        # Create a project first
        project_data = {
            "title": "Test Project",
            "description": "A test project",
            "status": "active",
            "health": "healthy"
        }
        project_response = client.post("/api/projects", json=project_data)
        project_id = project_response.json()["id"]

        # Create a user
        user_data = {"name": "John Doe", "email": "john@example.com"}
        user_response = client.post("/api/users", json=user_data)
        user_id = user_response.json()["id"]

        # Add team member
        team_member_data = {
            "user_id": user_id,
            "role": "developer",
            "capacity": 1.0
        }
        member_response = client.post(f"/api/projects/{project_id}/team-members", json=team_member_data)
        member_id = member_response.json()["id"]

        # Update capacity
        update_data = {"capacity": 0.5}
        response = client.put(f"/api/team-members/{member_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["capacity"] == 0.5


# ============================================
# WebSocket Tests
# ============================================
class TestWebSocket:
    def test_websocket_connection(self, client):
        """Test that WebSocket connection can be established."""
        with client.websocket_connect("/ws") as websocket:
            # Connection successful if no exception raised
            assert websocket is not None

    def test_websocket_receives_project_create(self, client):
        """Test that WebSocket receives notification on project creation."""
        with client.websocket_connect("/ws") as websocket:
            # Create a project via REST API
            project_data = {
                "title": "WebSocket Test Project",
                "description": "Testing WebSocket notifications",
                "status": "active",
                "health": "healthy",
                "owner": "Test Owner",
            }
            response = client.post("/api/projects", json=project_data)
            assert response.status_code == 200

            # WebSocket should receive the notification
            data = websocket.receive_json()
            assert data["type"] == "project_update"
            assert data["event_type"] == "created"
            assert data["data"]["title"] == "WebSocket Test Project"

    def test_websocket_receives_project_update(self, client):
        """Test that WebSocket receives notification on project update."""
        # Create a project first
        project_data = {
            "title": "Update Test Project",
            "description": "Testing update notifications",
            "status": "active",
            "health": "healthy"
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        with client.websocket_connect("/ws") as websocket:
            # Update the project
            update_data = {"title": "Updated via WebSocket Test"}
            client.put(f"/api/projects/{project_id}", json=update_data)

            # WebSocket should receive the notification
            data = websocket.receive_json()
            assert data["type"] == "project_update"
            assert data["event_type"] == "updated"
            assert data["project_id"] == project_id

    def test_websocket_receives_project_delete(self, client):
        """Test that WebSocket receives notification on project deletion."""
        # Create a project first
        project_data = {
            "title": "Delete Test Project",
            "description": "Testing delete notifications",
            "status": "active",
            "health": "healthy"
        }
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["id"]

        with client.websocket_connect("/ws") as websocket:
            # Delete the project
            client.delete(f"/api/projects/{project_id}")

            # WebSocket should receive the notification
            data = websocket.receive_json()
            assert data["type"] == "project_update"
            assert data["event_type"] == "deleted"
            assert data["project_id"] == project_id
