from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    score = Column(Float, nullable=False)  
    max_points = Column(Float, nullable=False) 
    earned_points = Column(Float, nullable=False)  
    is_passed = Column(Boolean, nullable=True)
    attempt_number = Column(Integer, default=1, nullable=False) 
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    student = relationship("Student", back_populates="scores")

    def __repr__(self):
        return f"<Score(id={self.id}, student_id={self.student_id}, score={self.score})>"
