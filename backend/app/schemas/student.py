from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudentCreate(BaseModel):
    grade_level: Optional[str] = None
    school_name: Optional[str] = None
    bio: Optional[str] = None


class StudentUpdate(BaseModel):
    grade_level: Optional[str] = None
    school_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    user_id: int
    cohort_id: Optional[int]
    grade_level: Optional[str]
    school_name: Optional[str]
    enrollment_date: datetime
    bio: Optional[str]
    profile_picture_url: Optional[str]

    class Config:
        from_attributes = True


class StudentDetailResponse(StudentResponse):
    user: Optional[dict] = None   
    cohort: Optional[dict] = None


class StudentListResponse(BaseModel):
    total: int
    students: list[StudentResponse]