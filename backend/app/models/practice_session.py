from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)

    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)


    score = Column(Float, nullable=True)

    ai_feedback = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    
    __table_args__ = (
        Index("idx_student_test", "student_id", "test_id"),
    )

    student = relationship("Student", back_populates="practice_sessions")
    test = relationship("Test", back_populates="practice_sessions")
    responses = relationship("Response", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PracticeSession(id={self.id}, student_id={self.student_id}, test_id={self.test_id})>"