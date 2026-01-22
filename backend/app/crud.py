from datetime import datetime

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app import models, schemas

def calculate_project_progress(db: Session, project_id: int) -> float:
    """Calculate project progress based on completed milestones"""
    milestones = db.query(models.Milestone).filter(models.Milestone.project_id == project_id).all()
    if not milestones:
        return 0.0
    completed = sum(1 for m in milestones if m.completed)
    return (completed / len(milestones)) * 100.0

def update_project_progress(db: Session, project_id: int):
    """Update project progress and save"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project:
        project.progress = calculate_project_progress(db, project_id)
        db.commit()

def create_project_event(db: Session, project_id: int, event_type: str, description: str):
    """Create a project event"""
    event = models.ProjectEvent(
        project_id=project_id,
        event_type=event_type,
        description=description
    )
    db.add(event)
    db.commit()
    return event

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# Tag CRUD
def get_or_create_tag(db: Session, tag_name: str):
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not tag:
        tag = models.Tag(name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag

def get_tags(db: Session):
    return db.query(models.Tag).all()

# Project CRUD
def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        title=project.title,
        description=project.description,
        short_description=project.short_description,
        owner_id=project.owner_id,
        status=project.status,
        health=project.health
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Add tags
    if project.tag_names:
        for tag_name in project.tag_names:
            tag = get_or_create_tag(db, tag_name)
            project_tag = models.ProjectTag(project_id=db_project.id, tag_id=tag.id)
            db.add(project_tag)

    db.commit()
    create_project_event(db, db_project.id, "project_created", f"Project '{db_project.title}' was created")
    return db_project

def get_project(db: Session, project_id: int, include_deleted: bool = False):
    query = db.query(models.Project).filter(models.Project.id == project_id)
    if not include_deleted:
        query = query.filter(models.Project.deleted_at is None)
    return query.first()

def get_projects(
    db: Session,
    filter_params: schemas.ProjectFilter,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "updated_at",
    sort_order: str = "desc"
):
    query = db.query(models.Project)

    # Soft delete filter
    if filter_params.only_deleted:
        # Show only deleted projects
        query = query.filter(models.Project.deleted_at is not None)
    elif not filter_params.include_deleted:
        # Exclude deleted projects (default)
        query = query.filter(models.Project.deleted_at is None)
    # else: include_deleted=True shows all projects

    # Status filter
    if filter_params.status:
        query = query.filter(models.Project.status == filter_params.status)

    # Owner filter
    if filter_params.owner_id:
        query = query.filter(models.Project.owner_id == filter_params.owner_id)

    # Health filter
    if filter_params.health:
        query = query.filter(models.Project.health == filter_params.health)

    # Tag filter
    if filter_params.tag_name:
        query = query.join(models.ProjectTag).join(models.Tag).filter(
            models.Tag.name == filter_params.tag_name
        )

    # Search query (full-text search across title, description, tags)
    if filter_params.search_query:
        search_term = f"%{filter_params.search_query}%"
        query = query.outerjoin(models.ProjectTag).outerjoin(models.Tag).filter(
            or_(
                models.Project.title.ilike(search_term),
                models.Project.description.ilike(search_term),
                models.Project.short_description.ilike(search_term),
                models.Tag.name.ilike(search_term)
            )
        ).distinct()

    # Sorting
    sort_column = getattr(models.Project, sort_by, models.Project.updated_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return items, total

def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate):
    db_project = get_project(db, project_id)
    if not db_project:
        return None

    # Optimistic concurrency check
    if project_update.version is not None and db_project.version != project_update.version:
        raise ValueError(f"Version mismatch. Expected {project_update.version}, got {db_project.version}")

    update_data = project_update.dict(exclude_unset=True, exclude={"tag_names", "version"})

    # Update tags if provided
    if "tag_names" in project_update.dict(exclude_unset=True):
        # Remove existing tags
        db.query(models.ProjectTag).filter(models.ProjectTag.project_id == project_id).delete()
        # Add new tags
        for tag_name in project_update.tag_names:
            tag = get_or_create_tag(db, tag_name)
            project_tag = models.ProjectTag(project_id=project_id, tag_id=tag.id)
            db.add(project_tag)

    for field, value in update_data.items():
        setattr(db_project, field, value)

    db_project.version += 1
    db.commit()
    db.refresh(db_project)

    # Create events for significant changes
    if project_update.status and project_update.status != db_project.status:
        create_project_event(db, project_id, "status_changed",
                           f"Status changed to {project_update.status.value}")

    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if db_project:
        db_project.deleted_at = datetime.utcnow()
        db.commit()
        create_project_event(db, project_id, "project_deleted",
                           f"Project '{db_project.title}' was soft deleted")
    return db_project

def recover_project(db: Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project and db_project.deleted_at:
        db_project.deleted_at = None
        db.commit()
        create_project_event(db, project_id, "project_recovered",
                           f"Project '{db_project.title}' was recovered")
    return db_project

def bulk_update_projects(db: Session, bulk_update: schemas.BulkUpdateRequest):
    """Bulk update projects with optimistic concurrency"""
    updated_count = 0
    failed_count = 0
    errors = []

    for project_id in bulk_update.project_ids:
        try:
            db_project = get_project(db, project_id, include_deleted=True)
            if not db_project:
                failed_count += 1
                errors.append(f"Project {project_id} not found")
                continue

            # Version check
            if bulk_update.version is not None and db_project.version != bulk_update.version:
                failed_count += 1
                errors.append(f"Project {project_id}: version mismatch")
                continue

            # Update status
            if bulk_update.status:
                db_project.status = bulk_update.status
                db_project.version += 1
                create_project_event(db, project_id, "status_changed",
                                   f"Status changed to {bulk_update.status.value}")

            # Update tags
            if bulk_update.tag_names is not None:
                db.query(models.ProjectTag).filter(models.ProjectTag.project_id == project_id).delete()
                for tag_name in bulk_update.tag_names:
                    tag = get_or_create_tag(db, tag_name)
                    project_tag = models.ProjectTag(project_id=project_id, tag_id=tag.id)
                    db.add(project_tag)
                db_project.version += 1

            updated_count += 1
        except Exception as e:
            failed_count += 1
            errors.append(f"Project {project_id}: {str(e)}")

    db.commit()
    return updated_count, failed_count, errors

# Milestone CRUD
def create_milestone(db: Session, milestone: schemas.MilestoneCreate, project_id: int):
    db_milestone = models.Milestone(**milestone.dict(), project_id=project_id)
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    update_project_progress(db, project_id)
    create_project_event(db, project_id, "milestone_created",
                        f"Milestone '{db_milestone.title}' was created")
    return db_milestone

def update_milestone(db: Session, milestone_id: int, milestone_update: schemas.MilestoneBase):
    db_milestone = db.query(models.Milestone).filter(models.Milestone.id == milestone_id).first()
    if db_milestone:
        update_data = milestone_update.dict(exclude_unset=True)
        was_completed = db_milestone.completed
        for field, value in update_data.items():
            setattr(db_milestone, field, value)
        db.commit()
        db.refresh(db_milestone)

        # Update project progress
        update_project_progress(db, db_milestone.project_id)

        # Create event if completion status changed
        if milestone_update.completed is not None and was_completed != milestone_update.completed:
            event_type = "milestone_completed" if milestone_update.completed else "milestone_reopened"
            create_project_event(db, db_milestone.project_id, event_type,
                               f"Milestone '{db_milestone.title}' was {'completed' if milestone_update.completed else 'reopened'}")
    return db_milestone

# Team Member CRUD
def add_team_member(db: Session, team_member: schemas.TeamMemberCreate, project_id: int):
    db_member = models.TeamMember(**team_member.dict(), project_id=project_id)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    user = get_user(db, team_member.user_id)
    create_project_event(db, project_id, "team_member_added",
                        f"{user.name} was added to the team as {team_member.role.value}")
    return db_member

def update_team_member(db: Session, member_id: int, member_update: schemas.TeamMemberUpdate):
    db_member = db.query(models.TeamMember).filter(models.TeamMember.id == member_id).first()
    if db_member is None:
        return None

    update_data = member_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_member, field, value)

    db.commit()
    db.refresh(db_member)

    user = get_user(db, db_member.user_id)
    create_project_event(db, db_member.project_id, "team_member_updated",
                        f"{user.name}'s role/capacity was updated")
    return db_member

def remove_team_member(db: Session, member_id: int):
    db_member = db.query(models.TeamMember).filter(models.TeamMember.id == member_id).first()
    if db_member:
        project_id = db_member.project_id
        user = get_user(db, db_member.user_id)
        db.delete(db_member)
        db.commit()
        create_project_event(db, project_id, "team_member_removed",
                           f"{user.name} was removed from the team")
    return db_member
