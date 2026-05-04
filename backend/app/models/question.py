from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.database import Base
from sqlalchemy.dialects.postgresql import JSON


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), default=QuestionType.MULTIPLE_CHOICE, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)  
    points = Column(Integer, default=1, nullable=False)
    order = Column(Integer, nullable=False)  
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    test = relationship("Test", back_populates="questions")
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question(id={self.id}, test_id={self.test_id})>"
