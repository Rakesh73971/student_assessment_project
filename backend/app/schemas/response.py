from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResponseCreate(BaseModel):
    question_id: int
    answer_text: str


class ResponseUpdate(BaseModel):
    answer_text: str


class ResponseDetail(BaseModel):
    id: int
    session_id: int
    question_id: int
    answer_text: str
    is_correct: Optional[bool]
    points_earned: Optional[float]
    ai_evaluation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True