"""Cohort schemas."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CohortCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CohortUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class StudentInCohort(BaseModel):
    id: int
    user_id: int
    enrollment_date: datetime

    class Config:
        from_attributes = True


class CohortResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    instructor_id: int
    created_at: datetime
    students_count: int = 0

    class Config:
        from_attributes = True


class CohortDetailResponse(CohortResponse):
    students: List[StudentInCohort] = []