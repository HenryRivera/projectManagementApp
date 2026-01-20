"""Initialize database with sample data"""
from app.database import SessionLocal, engine
from app import models, crud, schemas

# Create tables
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create sample users
users = [
    schemas.UserCreate(name="John Doe", email="john@example.com"),
    schemas.UserCreate(name="Jane Smith", email="jane@example.com"),
    schemas.UserCreate(name="Bob Johnson", email="bob@example.com"),
]

created_users = []
for user_data in users:
    existing = crud.get_user_by_email(db, user_data.email)
    if not existing:
        user = crud.create_user(db, user_data)
        created_users.append(user)
        print(f"Created user: {user.name}")
    else:
        created_users.append(existing)

# Create sample projects
projects = [
    schemas.ProjectCreate(
        title="E-commerce Platform",
        description="Build a modern e-commerce platform with React and Node.js",
        short_description="Modern e-commerce solution",
        owner_id=created_users[0].id,
        status=schemas.ProjectStatus.ACTIVE,
        health=schemas.ProjectHealth.HEALTHY,
        tag_names=["web", "react", "e-commerce"]
    ),
    schemas.ProjectCreate(
        title="Mobile App Redesign",
        description="Redesign the mobile app with new UI/UX",
        short_description="Mobile app UI/UX redesign",
        owner_id=created_users[1].id,
        status=schemas.ProjectStatus.ACTIVE,
        health=schemas.ProjectHealth.AT_RISK,
        tag_names=["mobile", "design", "ios", "android"]
    ),
    schemas.ProjectCreate(
        title="API Migration",
        description="Migrate legacy API to microservices architecture",
        short_description="Legacy API migration",
        owner_id=created_users[0].id,
        status=schemas.ProjectStatus.PLANNING,
        health=schemas.ProjectHealth.HEALTHY,
        tag_names=["backend", "api", "microservices"]
    ),
]

created_projects = []
for project_data in projects:
    project = crud.create_project(db, project_data)
    created_projects.append(project)
    print(f"Created project: {project.title}")

# Add milestones to first project
if created_projects:
    milestones = [
        schemas.MilestoneCreate(title="Design Phase", description="Complete UI/UX design", completed=True),
        schemas.MilestoneCreate(title="Development Phase", description="Implement core features", completed=False),
        schemas.MilestoneCreate(title="Testing Phase", description="QA and testing", completed=False),
    ]
    for milestone_data in milestones:
        crud.create_milestone(db, milestone_data, created_projects[0].id)

# Add team members
if created_projects and created_users:
    team_members = [
        schemas.TeamMemberCreate(user_id=created_users[1].id, role=schemas.UserRole.DEVELOPER, capacity=0.5),
        schemas.TeamMemberCreate(user_id=created_users[2].id, role=schemas.UserRole.DESIGNER, capacity=1.0),
    ]
    for member_data in team_members:
        crud.add_team_member(db, member_data, created_projects[0].id)

print("\nDatabase initialized with sample data!")
