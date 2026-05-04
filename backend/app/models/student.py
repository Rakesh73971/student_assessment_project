from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    cohort_id = Column(
        Integer,
        ForeignKey("cohorts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    grade_level = Column(String(50), nullable=True)
    school_name = Column(String(255), nullable=True)
    enrollment_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    user = relationship("User", back_populates="student_profile")
    cohort = relationship("Cohort", back_populates="students")
    practice_sessions = relationship(
        "PracticeSession",
        back_populates="student",
        cascade="all, delete-orphan"
    )
    scores = relationship(
        "Score",
        back_populates="student",
        cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<Student(id={self.id}, user_id={self.user_id})>"