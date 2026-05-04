from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging
from typing import Optional, Dict, Any

from app.models.student import Student

logger = logging.getLogger(__name__)


class StudentService:
    @staticmethod
    def get_student_profile(db: Session, student_id: int) -> Student:
        
        student = db.query(Student).filter(Student.id == student_id).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        return student

    @staticmethod
    def get_student_by_user(db: Session, user_id: int) -> Student:
        student = db.query(Student).filter(Student.user_id == user_id).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )

        return student

    @staticmethod
    def update_student_profile(
        db: Session,
        student_id: int,
        grade_level: Optional[str] = None,
        school_name: Optional[str] = None,
        bio: Optional[str] = None,
        profile_picture_url: Optional[str] = None
    ) -> Student:
        student = StudentService.get_student_profile(db, student_id)

        try:
            if grade_level is not None:
                student.grade_level = grade_level

            if school_name is not None:
                student.school_name = school_name

            if bio is not None:
                student.bio = bio

            if profile_picture_url is not None:
                student.profile_picture_url = profile_picture_url

            db.commit()
            db.refresh(student)

            logger.info(f"Student profile updated: {student_id}")

            return student

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating student {student_id}: {e}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update student profile"
            )

    @staticmethod
    def list_students_in_cohort(
        db: Session,
        cohort_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:

        query = db.query(Student).filter(Student.cohort_id == cohort_id)

        students = query.offset(skip).limit(limit).all()
        total = query.count()

        return {
            "total": total,
            "students": students
        }