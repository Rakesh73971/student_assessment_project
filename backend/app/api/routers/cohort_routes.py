from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.api.deps import get_db, get_current_user, get_current_instructor
from app.models.cohort import Cohort
from app.models.student import Student
from app.models.user import User, UserRole

from app.schemas.cohort import (
    CohortCreate,
    CohortUpdate,
    CohortResponse,
    CohortDetailResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cohorts", tags=["Cohorts"])


# =========================
# CREATE
# =========================

@router.post("/", response_model=CohortResponse)
def create_cohort(
    cohort_data: CohortCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    try:
        cohort = Cohort(
            name=cohort_data.name,
            description=cohort_data.description,
            instructor_id=current_user.id
        )

        db.add(cohort)
        db.commit()
        db.refresh(cohort)

        return cohort

    except Exception as e:
        db.rollback()
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Failed to create cohort")


# =========================
# LIST
# =========================

@router.get("/", response_model=list[CohortResponse])
def list_cohorts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(
        Cohort,
        func.count(Student.id).label("students_count")
    ).outerjoin(Student, Student.cohort_id == Cohort.id) \
     .group_by(Cohort.id)

    if current_user.role == UserRole.INSTRUCTOR:
        query = query.filter(Cohort.instructor_id == current_user.id)

    results = query.offset(skip).limit(limit).all()

    cohorts = []
    for cohort, count in results:
        cohort.students_count = count
        cohorts.append(cohort)

    return cohorts


# =========================
# DETAIL
# =========================

@router.get("/{cohort_id}", response_model=CohortDetailResponse)
def get_cohort(
    cohort_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cohort = db.get(Cohort, cohort_id)

    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found")

    if current_user.role == UserRole.INSTRUCTOR and cohort.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    students = db.query(Student).filter(Student.cohort_id == cohort_id).all()

    cohort.students = students
    cohort.students_count = len(students)

    return cohort


# =========================
# UPDATE
# =========================

@router.put("/{cohort_id}", response_model=CohortResponse)
def update_cohort(
    cohort_id: int,
    cohort_data: CohortUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    try:
        cohort = db.get(Cohort, cohort_id)

        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")

        if cohort.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not allowed")

        if cohort_data.name is not None:
            cohort.name = cohort_data.name

        if cohort_data.description is not None:
            cohort.description = cohort_data.description

        db.commit()
        db.refresh(cohort)

        return cohort

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Update failed")


# =========================
# DELETE
# =========================

@router.delete("/{cohort_id}", status_code=204)
def delete_cohort(
    cohort_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    try:
        cohort = db.get(Cohort, cohort_id)

        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")

        if cohort.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not allowed")

        db.delete(cohort)
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Delete failed")


# =========================
# ADD STUDENT
# =========================

@router.post("/{cohort_id}/students/{student_id}", status_code=204)
def add_student_to_cohort(
    cohort_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    try:
        cohort = db.get(Cohort, cohort_id)
        student = db.get(Student, student_id)

        if not cohort or not student:
            raise HTTPException(status_code=404, detail="Not found")

        if cohort.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not allowed")

        if student.cohort_id == cohort_id:
            raise HTTPException(status_code=400, detail="Already assigned")

        student.cohort_id = cohort_id
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Failed to add student")


# =========================
# REMOVE STUDENT
# =========================

@router.delete("/{cohort_id}/students/{student_id}", status_code=204)
def remove_student_from_cohort(
    cohort_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    try:
        cohort = db.get(Cohort, cohort_id)
        student = db.get(Student, student_id)

        if not cohort or not student:
            raise HTTPException(status_code=404, detail="Not found")

        if cohort.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not allowed")

        if student.cohort_id != cohort_id:
            raise HTTPException(status_code=400, detail="Not in this cohort")

        student.cohort_id = None
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Failed to remove student")