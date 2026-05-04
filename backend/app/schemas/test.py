from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"


class TestType(str, Enum):
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    QUIZ = "quiz"


class QuestionCreate(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int = 1
    order: int


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]]
    explanation: Optional[str]
    points: int
    order: int

    class Config:
        from_attributes = True


class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    duration_minutes: Optional[int] = None
    passing_score: int = 70
    test_type: TestType = TestType.PRACTICE
    cohort_id: Optional[int] = None
    questions: List[QuestionCreate] = Field(default_factory=list)


class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    duration_minutes: Optional[int] = None
    passing_score: Optional[int] = None
    is_published: Optional[bool] = None


class TestResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    cohort_id: Optional[int]
    test_type: TestType
    subject: Optional[str]
    duration_minutes: Optional[int]
    passing_score: int
    is_published: bool
    created_at: datetime
    questions_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TestDetailResponse(TestResponse):
    questions: List[QuestionResponse] = Field(default_factory=list)


class PracticeSessionStart(BaseModel):
    test_id: int


class ResponseSubmit(BaseModel):
    question_id: int
    answer_text: str


class TestResultsResponse(BaseModel):
    session_id: int
    test_id: int
    score: float
    passed: bool
    ai_feedback: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True