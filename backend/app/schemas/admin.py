"""Admin schemas."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


# =========================
# USER SCHEMAS
# =========================

class UserListResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserListResponse):
    last_login: Optional[datetime]
    bio: Optional[str]


# =========================
# UPDATE SCHEMAS
# =========================

class UpdateUserRole(BaseModel):
    role: UserRole


class UpdateUserStatus(BaseModel):
    is_active: bool


# =========================
# PAGINATION SCHEMA
# =========================

class PaginatedUsers(BaseModel):
    total: int
    users: List[UserListResponse]


# =========================
# STATS SCHEMAS
# =========================

class StatsOverview(BaseModel):
    total_users: int
    total_students: int
    total_instructors: int
    active_users: int
    inactive_users: int


class StudentStats(BaseModel):
    total_students: int
    students_with_attempts: int
    average_score: float