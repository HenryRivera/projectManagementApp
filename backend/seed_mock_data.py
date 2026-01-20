#!/usr/bin/env python3
"""
Seed script to populate the database with comprehensive mock data
including various edge cases for testing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
import random

def clear_existing_data(db: Session):
    """Clear existing data for a fresh start"""
    db.query(models.ProjectEvent).delete()
    db.query(models.TeamMember).delete()
    db.query(models.Milestone).delete()
    db.query(models.ProjectTag).delete()
    db.query(models.Tag).delete()
    db.query(models.Project).delete()
    db.query(models.User).delete()
    db.commit()

def seed_users(db: Session):
    """Create diverse set of users"""
    users_data = [
        {"name": "Alice Johnson", "email": "alice.johnson@example.com"},
        {"name": "Bob Smith", "email": "bob.smith@example.com"},
        {"name": "Carlos García", "email": "carlos.garcia@example.com"},  # Unicode name
        {"name": "Diana O'Brien", "email": "diana.obrien@example.com"},  # Apostrophe in name
        {"name": "李明", "email": "li.ming@example.com"},  # Chinese characters
        {"name": "François Müller", "email": "francois.muller@example.com"},  # Accented chars
        {"name": "Sarah Connor-Williams", "email": "sarah.cw@example.com"},  # Hyphenated
        {"name": "Dr. James Watson III", "email": "jwatson@example.com"},  # Title and suffix
        {"name": "A", "email": "a@b.co"},  # Minimal name
        {"name": "Bartholomew Christopher Montgomery-Fitzwilliam", "email": "long.name@example.com"},  # Very long name
    ]

    users = []
    for data in users_data:
        user = models.User(**data)
        db.add(user)
        users.append(user)
    db.commit()

    for user in users:
        db.refresh(user)

    return users

def seed_tags(db: Session):
    """Create diverse set of tags"""
    tag_names = [
        # Standard tags
        "frontend", "backend", "api", "database", "devops",
        # Priority tags
        "urgent", "low-priority", "critical",
        # Quarter tags
        "Q1-2026", "Q2-2026", "Q3-2026", "Q4-2026",
        # Technology tags
        "react", "python", "kubernetes", "aws", "postgresql",
        # Status-related
        "needs-review", "blocked", "ready-for-qa",
        # Edge cases
        "tag-with-dashes", "tag_with_underscores",
        "🚀 launch", "日本語タグ",  # Emoji and Japanese
        "a",  # Single char
        "this-is-a-very-long-tag-name-for-testing-purposes",  # Long tag
    ]

    tags = []
    for name in tag_names:
        tag = models.Tag(name=name)
        db.add(tag)
        tags.append(tag)
    db.commit()

    for tag in tags:
        db.refresh(tag)

    return tags

def seed_projects(db: Session, users: list, tags: list):
    """Create projects with various edge cases"""
    projects_data = [
        # Normal projects with various statuses
        {
            "title": "E-Commerce Platform Redesign",
            "description": "Complete overhaul of the customer-facing e-commerce platform including new checkout flow, improved search, and mobile optimization.",
            "short_description": "Modernizing our e-commerce platform",
            "status": models.ProjectStatus.ACTIVE,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 45.5,
            "owner_idx": 0,
            "tag_indices": [0, 1, 5, 11],
        },
        {
            "title": "API Gateway Migration",
            "description": "Migrate from legacy API gateway to Kong. This includes:\n\n- Route configuration\n- Auth plugin setup\n- Rate limiting\n- Monitoring integration\n\n**Important:** Maintain backward compatibility.",
            "short_description": "Kong API Gateway migration project",
            "status": models.ProjectStatus.ACTIVE,
            "health": models.ProjectHealth.AT_RISK,
            "progress": 72.0,
            "owner_idx": 1,
            "tag_indices": [1, 2, 4, 14],
        },
        {
            "title": "Mobile App v2.0",
            "description": "Next major version of our mobile application with new features and performance improvements.",
            "short_description": "Mobile app major version upgrade",
            "status": models.ProjectStatus.PLANNING,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 0.0,
            "owner_idx": 2,
            "tag_indices": [0, 7, 11],
        },
        {
            "title": "Database Performance Optimization",
            "description": "Identify and fix slow queries, add proper indexing, and implement caching strategies.",
            "short_description": "DB performance improvements",
            "status": models.ProjectStatus.COMPLETED,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 100.0,
            "owner_idx": 3,
            "tag_indices": [3, 14],
        },
        {
            "title": "Security Audit Remediation",
            "description": "Address all findings from the Q4 security audit including:\n\n1. XSS vulnerabilities\n2. SQL injection risks\n3. Authentication improvements\n4. Secrets management",
            "short_description": "Fix security audit findings",
            "status": models.ProjectStatus.ACTIVE,
            "health": models.ProjectHealth.CRITICAL,
            "progress": 25.0,
            "owner_idx": 4,
            "tag_indices": [1, 6, 17],
        },
        # Edge cases
        {
            "title": "A",  # Minimal title
            "description": None,  # No description
            "short_description": None,
            "status": models.ProjectStatus.PLANNING,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 0.0,
            "owner_idx": None,  # No owner
            "tag_indices": [],  # No tags
        },
        {
            "title": "Project with Unicode: 日本語プロジェクト 🎉",
            "description": "This project tests Unicode support including:\n\n- Japanese: こんにちは世界\n- Chinese: 你好世界\n- Emoji: 🚀 🎯 ✅ ❌ 🔥\n- Arabic: مرحبا بالعالم\n- Russian: Привет мир",
            "short_description": "Testing Unicode support 🌍",
            "status": models.ProjectStatus.ACTIVE,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 50.0,
            "owner_idx": 4,
            "tag_indices": [20, 21],
        },
        {
            "title": "Very Long Project Title That Goes On And On And Might Cause Layout Issues In The UI If Not Properly Handled With Ellipsis Or Wrapping",
            "description": "A" * 5000,  # Very long description
            "short_description": "Testing long content handling",
            "status": models.ProjectStatus.ON_HOLD,
            "health": models.ProjectHealth.AT_RISK,
            "progress": 33.33,
            "owner_idx": 9,
            "tag_indices": [22],
        },
        {
            "title": "Project <script>alert('xss')</script>",  # XSS test
            "description": "<b>Bold</b> <i>Italic</i> <script>alert('xss')</script> & < > \" '",
            "short_description": "Testing HTML/XSS handling",
            "status": models.ProjectStatus.PLANNING,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 0.0,
            "owner_idx": 0,
            "tag_indices": [0, 1],
        },
        {
            "title": "Cancelled Legacy System",
            "description": "This project was cancelled due to budget constraints.",
            "short_description": "Cancelled project",
            "status": models.ProjectStatus.CANCELLED,
            "health": models.ProjectHealth.CRITICAL,
            "progress": 15.0,
            "owner_idx": 1,
            "tag_indices": [7],
        },
        {
            "title": "Infrastructure Modernization",
            "description": "Moving to Kubernetes and implementing GitOps workflows.",
            "short_description": "K8s migration",
            "status": models.ProjectStatus.ACTIVE,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 60.0,
            "owner_idx": 5,
            "tag_indices": [4, 12, 13],
        },
        {
            "title": "Customer Feedback Portal",
            "description": "New portal for collecting and managing customer feedback.",
            "short_description": "Feedback collection system",
            "status": models.ProjectStatus.ACTIVE,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 80.0,
            "owner_idx": 6,
            "tag_indices": [0, 1, 18],
        },
        {
            "title": "Data Analytics Pipeline",
            "description": "Building a new data pipeline for real-time analytics.",
            "short_description": "Real-time analytics",
            "status": models.ProjectStatus.PLANNING,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 5.0,
            "owner_idx": 7,
            "tag_indices": [1, 3, 13],
        },
        {
            "title": "Deleted Project (Should Be Recoverable)",
            "description": "This project was soft-deleted for testing recovery.",
            "short_description": "Soft-deleted project",
            "status": models.ProjectStatus.ON_HOLD,
            "health": models.ProjectHealth.AT_RISK,
            "progress": 40.0,
            "owner_idx": 8,
            "tag_indices": [16],
            "deleted": True,
        },
        {
            "title": "Zero Progress Active Project",
            "description": "Just started, no progress yet.",
            "short_description": "Brand new project",
            "status": models.ProjectStatus.ACTIVE,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 0.0,
            "owner_idx": 0,
            "tag_indices": [8],
        },
        {
            "title": "Project with All Tag Types",
            "description": "Testing project with many different tag types.",
            "short_description": "Multi-tag test",
            "status": models.ProjectStatus.ACTIVE,
            "health": models.ProjectHealth.HEALTHY,
            "progress": 55.5,
            "owner_idx": 1,
            "tag_indices": list(range(10)),  # First 10 tags
        },
    ]

    projects = []
    for data in projects_data:
        owner_id = users[data["owner_idx"]].id if data.get("owner_idx") is not None else None

        project = models.Project(
            title=data["title"],
            description=data["description"],
            short_description=data["short_description"],
            status=data["status"],
            health=data["health"],
            progress=data["progress"],
            owner_id=owner_id,
        )

        if data.get("deleted"):
            project.deleted_at = datetime.utcnow() - timedelta(days=7)

        db.add(project)
        db.flush()  # Get the ID

        # Add tags
        for tag_idx in data.get("tag_indices", []):
            if tag_idx < len(tags):
                project_tag = models.ProjectTag(project_id=project.id, tag_id=tags[tag_idx].id)
                db.add(project_tag)

        projects.append(project)

    db.commit()

    for project in projects:
        db.refresh(project)

    return projects

def seed_milestones(db: Session, projects: list):
    """Add milestones to projects with various states"""
    milestone_templates = [
        # Project 0: E-Commerce (45.5% progress)
        [
            {"title": "Requirements gathering", "completed": True, "days_offset": -30},
            {"title": "UI/UX Design", "completed": True, "days_offset": -15},
            {"title": "Frontend development", "completed": False, "days_offset": 15},
            {"title": "Backend API development", "completed": False, "days_offset": 20},
            {"title": "Testing & QA", "completed": False, "days_offset": 30},
            {"title": "Deployment", "completed": False, "days_offset": 45},
        ],
        # Project 1: API Gateway (72% progress)
        [
            {"title": "Architecture review", "completed": True, "days_offset": -45},
            {"title": "Kong installation", "completed": True, "days_offset": -30},
            {"title": "Route migration", "completed": True, "days_offset": -15},
            {"title": "Auth plugin setup", "completed": False, "days_offset": 5, "description": "⚠️ Blocked on security team review"},
            {"title": "Performance testing", "completed": False, "days_offset": 15},
        ],
        # Project 4: Security Audit (25% progress, critical)
        [
            {"title": "XSS vulnerability fixes", "completed": True, "days_offset": -5},
            {"title": "SQL injection remediation", "completed": False, "days_offset": 3, "description": "URGENT: Production risk"},
            {"title": "Auth improvements", "completed": False, "days_offset": 10},
            {"title": "Secrets management", "completed": False, "days_offset": 20},
        ],
        # Project 6: Unicode project
        [
            {"title": "マイルストーン 1 🎯", "completed": True, "days_offset": -10},
            {"title": "里程碑 2 ✅", "completed": False, "days_offset": 10},
            {"title": "Milestone with émojis 🚀🎉", "completed": False, "days_offset": 20},
        ],
        # Project 11: Customer Feedback (80% progress)
        [
            {"title": "Design mockups", "completed": True, "days_offset": -60},
            {"title": "Database schema", "completed": True, "days_offset": -50},
            {"title": "API endpoints", "completed": True, "days_offset": -30},
            {"title": "Frontend components", "completed": True, "days_offset": -15},
            {"title": "Integration testing", "completed": False, "days_offset": 5},
        ],
    ]

    project_indices = [0, 1, 4, 6, 11]

    for proj_idx, milestones in zip(project_indices, milestone_templates):
        if proj_idx >= len(projects):
            continue
        project = projects[proj_idx]

        for m in milestones:
            due_date = datetime.utcnow() + timedelta(days=m["days_offset"])
            milestone = models.Milestone(
                project_id=project.id,
                title=m["title"],
                description=m.get("description"),
                completed=m["completed"],
                due_date=due_date,
            )
            db.add(milestone)

    db.commit()

def seed_team_members(db: Session, projects: list, users: list):
    """Add team members with various roles and capacities"""
    team_assignments = [
        # Project 0: E-Commerce
        {"project_idx": 0, "user_idx": 0, "role": models.UserRole.OWNER, "capacity": 1.0},
        {"project_idx": 0, "user_idx": 1, "role": models.UserRole.DEVELOPER, "capacity": 1.0},
        {"project_idx": 0, "user_idx": 2, "role": models.UserRole.DEVELOPER, "capacity": 0.5},
        {"project_idx": 0, "user_idx": 6, "role": models.UserRole.DESIGNER, "capacity": 0.75},
        {"project_idx": 0, "user_idx": 8, "role": models.UserRole.QA, "capacity": 0.25},

        # Project 1: API Gateway
        {"project_idx": 1, "user_idx": 1, "role": models.UserRole.OWNER, "capacity": 0.8},
        {"project_idx": 1, "user_idx": 4, "role": models.UserRole.DEVELOPER, "capacity": 1.0},
        {"project_idx": 1, "user_idx": 5, "role": models.UserRole.MANAGER, "capacity": 0.3},

        # Project 4: Security
        {"project_idx": 4, "user_idx": 4, "role": models.UserRole.OWNER, "capacity": 1.0},
        {"project_idx": 4, "user_idx": 0, "role": models.UserRole.DEVELOPER, "capacity": 0.5},
        {"project_idx": 4, "user_idx": 1, "role": models.UserRole.DEVELOPER, "capacity": 0.5},

        # Project 6: Unicode
        {"project_idx": 6, "user_idx": 4, "role": models.UserRole.OWNER, "capacity": 1.0},

        # Project 10: Infrastructure
        {"project_idx": 10, "user_idx": 5, "role": models.UserRole.OWNER, "capacity": 1.0},
        {"project_idx": 10, "user_idx": 3, "role": models.UserRole.DEVELOPER, "capacity": 1.0},
    ]

    for assignment in team_assignments:
        if assignment["project_idx"] >= len(projects) or assignment["user_idx"] >= len(users):
            continue

        team_member = models.TeamMember(
            project_id=projects[assignment["project_idx"]].id,
            user_id=users[assignment["user_idx"]].id,
            role=assignment["role"],
            capacity=assignment["capacity"],
        )
        db.add(team_member)

    db.commit()

def seed_events(db: Session, projects: list):
    """Add project events/history"""
    event_templates = [
        {"project_idx": 0, "event_type": "project_created", "description": "Project was created", "days_ago": 60},
        {"project_idx": 0, "event_type": "status_changed", "description": "Status changed from planning to active", "days_ago": 45},
        {"project_idx": 0, "event_type": "milestone_completed", "description": "Completed: Requirements gathering", "days_ago": 30},
        {"project_idx": 0, "event_type": "team_member_added", "description": "Added Bob Smith as Developer", "days_ago": 40},

        {"project_idx": 1, "event_type": "project_created", "description": "Project was created", "days_ago": 90},
        {"project_idx": 1, "event_type": "health_changed", "description": "Health changed to at_risk due to delays", "days_ago": 10},

        {"project_idx": 4, "event_type": "project_created", "description": "Project was created after security audit", "days_ago": 30},
        {"project_idx": 4, "event_type": "health_changed", "description": "Health changed to critical - vulnerabilities found in production", "days_ago": 5},

        {"project_idx": 9, "event_type": "project_created", "description": "Project was created", "days_ago": 180},
        {"project_idx": 9, "event_type": "status_changed", "description": "Status changed to cancelled", "days_ago": 30},
    ]

    for event in event_templates:
        if event["project_idx"] >= len(projects):
            continue

        project_event = models.ProjectEvent(
            project_id=projects[event["project_idx"]].id,
            event_type=event["event_type"],
            description=event["description"],
            created_at=datetime.utcnow() - timedelta(days=event["days_ago"]),
        )
        db.add(project_event)

    db.commit()

def main():
    print("🌱 Starting database seed...")

    db = SessionLocal()

    try:
        print("  Clearing existing data...")
        clear_existing_data(db)

        print("  Creating users...")
        users = seed_users(db)
        print(f"    ✓ Created {len(users)} users")

        print("  Creating tags...")
        tags = seed_tags(db)
        print(f"    ✓ Created {len(tags)} tags")

        print("  Creating projects...")
        projects = seed_projects(db, users, tags)
        print(f"    ✓ Created {len(projects)} projects")

        print("  Creating milestones...")
        seed_milestones(db, projects)
        print("    ✓ Created milestones")

        print("  Creating team members...")
        seed_team_members(db, projects, users)
        print("    ✓ Created team members")

        print("  Creating project events...")
        seed_events(db, projects)
        print("    ✓ Created events")

        print("\n✅ Database seeded successfully!")
        print(f"\nSummary:")
        print(f"  - {len(users)} users")
        print(f"  - {len(tags)} tags")
        print(f"  - {len(projects)} projects (1 soft-deleted)")
        print(f"  - Various milestones, team members, and events")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
