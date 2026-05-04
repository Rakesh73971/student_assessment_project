from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.database import Base


class TestType(str, enum.Enum):
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    QUIZ = "quiz"


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    cohort_id = Column(Integer, ForeignKey("cohorts.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_type = Column(Enum(TestType), default=TestType.PRACTICE, nullable=False)
    subject = Column(String(100), nullable=True)
    duration_minutes = Column(Integer, nullable=True)  
    passing_score = Column(Integer, default=70, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    cohort = relationship("Cohort", back_populates="tests")
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeSession", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Test(id={self.id}, title={self.title})>"
