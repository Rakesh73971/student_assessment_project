"""Admin management routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_admin
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.score import Score

from app.schemas.admin import (
    UserListResponse,
    UserDetailResponse,
    UpdateUserRole,
    UpdateUserStatus,
    PaginatedUsers,
    StatsOverview,
    StudentStats
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


# =========================
# USERS
# =========================

@router.get("/users", response_model=PaginatedUsers)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role: UserRole = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()

    users = (
        query.order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"total": total, "users": users}


@router.get("/users/{user_id}", response_model=UserDetailResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/users/{user_id}/role", response_model=UserDetailResponse)
def update_user_role(
    user_id: int,
    role_data: UpdateUserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    try:
        user.role = role_data.role
        db.commit()
        db.refresh(user)

        logger.info(f"User {user_id} role updated")
        return user

    except Exception as e:
        db.rollback()
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Failed to update role")


@router.put("/users/{user_id}/status", response_model=UserDetailResponse)
def update_user_status(
    user_id: int,
    status_data: UpdateUserStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    user.is_active = status_data.is_active

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    db.delete(user)
    db.commit()


# =========================
# STATS
# =========================

@router.get("/stats/overview", response_model=StatsOverview)
def get_stats_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    total_instructors = db.query(User).filter(User.role == UserRole.INSTRUCTOR).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_instructors": total_instructors,
        "active_users": active_users,
        "inactive_users": total_users - active_users
    }


@router.get("/stats/students", response_model=StudentStats)
def get_student_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    total_students = db.query(Student).count()

    students_with_scores = db.query(
        func.count(func.distinct(Score.student_id))
    ).scalar() or 0

    avg_score = db.query(func.avg(Score.score)).scalar() or 0

    return {
        "total_students": total_students,
        "students_with_attempts": students_with_scores,
        "average_score": round(avg_score, 2)
    }