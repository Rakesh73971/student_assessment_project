from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_student
from app.schemas.student import (
    StudentUpdate,
    StudentResponse,
    StudentListResponse
)
from app.services.student_services import StudentService
from app.models.user import User
from app.models.student import Student

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/students", tags=["Students"])


@router.get("/me", response_model=StudentResponse)
def get_my_profile(
    student: Student = Depends(get_current_student),
):
    
    return student


@router.put("/me", response_model=StudentResponse)
def update_my_profile(
    profile_data: StudentUpdate,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    
    return StudentService.update_student_profile(
        db=db,
        student_id=student.id,
        grade_level=profile_data.grade_level,
        school_name=profile_data.school_name,
        bio=profile_data.bio,
        profile_picture_url=profile_data.profile_picture_url
    )


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    

    student = StudentService.get_student_profile(db, student_id)

    if student.user_id != current_user.id and current_user.role.value == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this profile"
        )

    return student


@router.get("/cohort/{cohort_id}", response_model=StudentListResponse)
def list_students_in_cohort(
    cohort_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    

    if current_user.role.value == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view cohort students"
        )

    return StudentService.list_students_in_cohort(db, cohort_id, skip, limit)