from sqlalchemy import Column, Integer, ForeignKey, Text, Float, Boolean, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("practice_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id = Column(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

   
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="unique_response_per_question"),
    )

    
    session = relationship("PracticeSession", back_populates="responses")
    question = relationship("Question", back_populates="responses")

    def __repr__(self):
        return f"<Response(id={self.id}, session_id={self.session_id}, question_id={self.question_id})>"
