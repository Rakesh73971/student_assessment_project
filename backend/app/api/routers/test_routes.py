from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    get_current_user,
    get_current_student,
    get_current_instructor
)

from app.schemas.test import (
    TestCreate,
    TestUpdate,
    TestResponse,
    TestDetailResponse,
    PracticeSessionStart,
    ResponseSubmit,
    TestResultsResponse,
    QuestionCreate,
    QuestionResponse
)

from app.services.test_services import TestService
from app.services.ai_service import AIService

from app.models.user import User
from app.models.student import Student
from app.models.practice_session import PracticeSession
from app.models.response import Response
from app.models.test import Test
from app.models.question import Question

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tests", tags=["Tests & Practice"])
ai_service = AIService()


# ==================== LIST TESTS ====================


@router.get("/", response_model=list[TestResponse])
def list_tests(
    cohort_id: int | None = None,
    only_published: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Test)

    if cohort_id is not None:
        query = query.filter(Test.cohort_id == cohort_id)

    if only_published:
        query = query.filter(Test.is_published == True)

    tests = query.offset(skip).limit(limit).all()
    return tests


@router.get("/my", response_model=list[TestResponse])
def list_my_tests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    

    tests = db.query(Test).filter(Test.created_by == current_user.id).all()

    return tests



# ==================== TEST MANAGEMENT ====================

@router.post("/", response_model=TestResponse)
def create_test(
    test_data: TestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
   
    try:
        test = TestService.create_test(
            db=db,
            title=test_data.title,
            description=test_data.description,
            cohort_id=test_data.cohort_id,
            created_by=current_user.id,
            test_type=test_data.test_type,
            subject=test_data.subject,
            duration_minutes=test_data.duration_minutes,
            passing_score=test_data.passing_score
        )

        
        for i, q in enumerate(test_data.questions or []):
            TestService.add_question_to_test(
                db=db,
                test_id=test.id,
                question_text=q.question_text,
                question_type=q.question_type,
                correct_answer=q.correct_answer,
                options=q.options,
                explanation=q.explanation,
                points=q.points,
                order=i + 1
            )

        return test

    except HTTPException:
        
        raise
    except Exception as e:
        logger.error(f"Create test error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create test")


@router.get("/{test_id}", response_model=TestDetailResponse)
def get_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):


    test = TestService.get_test(db, test_id)

    if not test.is_published and current_user.role.value == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test is not yet published"
        )

    return test



@router.get("/sessions/{session_id}")
def get_session_details(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):


    session = db.query(PracticeSession).filter(PracticeSession.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")


    if current_user.role.value == "student":
        if session.student.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    
    responses = [
        {
            "id": r.id,
            "question_id": r.question_id,
            "question_text": (r.question.question_text if r.question else None),
            "answer_text": r.answer_text,
            "is_correct": r.is_correct,
            "points_earned": r.points_earned
        }
        for r in session.responses
    ]

    test = session.test
    return {
        "session_id": session.id,
        "test_id": session.test_id,
        "student_id": session.student_id,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "score": session.score,
        "passing_score": test.passing_score if test else None,
        "test_title": test.title if test else None,
        "ai_feedback": session.ai_feedback,
        "responses": responses,
        "created_at": session.created_at
    }


@router.put("/{test_id}", response_model=TestResponse)
def update_test(
    test_id: int,
    test_data: TestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    """Update test."""

    test = TestService.get_test(db, test_id)

    if test.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission"
        )

    update_fields = test_data.dict(exclude_unset=True)

    for key, value in update_fields.items():
        setattr(test, key, value)

    db.commit()
    db.refresh(test)

    return test


@router.post("/{test_id}/questions", response_model=QuestionResponse)
def add_question(
    test_id: int,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    """Add question."""

    try:
        test = TestService.get_test(db, test_id)

        if test.created_by != current_user.id and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        return TestService.add_question_to_test(
            db=db,
            test_id=test_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            correct_answer=question_data.correct_answer,
            options=question_data.options,
            explanation=question_data.explanation,
            points=question_data.points,
            order=question_data.order
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add question error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add question")


# ==================== PRACTICE ====================

@router.post("/sessions/start")
def start_practice_session(
    session_data: PracticeSessionStart,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student)
):
    session = TestService.start_practice_session(
        db=db,
        student_id=student.id,
        test_id=session_data.test_id
    )

    return {
        "session_id": session.id,
        "test_id": session.test_id,
        "started_at": session.started_at
    }


@router.post("/sessions/{session_id}/submit-response")
def submit_response(
    session_id: int,
    response_data: ResponseSubmit,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student)
):
    response = TestService.submit_response(
        db=db,
        session_id=session_id,
        question_id=response_data.question_id,
        student_id=student.id,
        answer_text=response_data.answer_text
    )

    return {
        "response_id": response.id,
        "question_id": response.question_id,
        "submitted_at": response.created_at
    }


@router.post("/sessions/{session_id}/complete", response_model=TestResultsResponse)
def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student)
):
    session = db.query(PracticeSession).filter(
        PracticeSession.id == session_id,
        PracticeSession.student_id == student.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    completed = TestService.complete_session(db, session_id)

    ai_feedback = None

    try:
        responses = db.query(Response).filter(
            Response.session_id == session_id
        ).all()

        if responses:
            student_answers = [
                {
                    "question_text": r.question.question_text,
                    "student_answer": r.answer_text,
                    "is_correct": r.is_correct
                }
                for r in responses
            ]

            ai_feedback = ai_service.generate_feedback(
                student_answers=student_answers,
                test_title=completed.test.title,
                overall_score=completed.score or 0
            )

            completed.ai_feedback = ai_feedback
            db.commit()

    except Exception as e:
        logger.error(f"AI feedback error: {e}")

    return {
        "session_id": completed.id,
        "test_id": completed.test_id,
        "score": completed.score,
        "passed": (completed.score or 0) >= completed.test.passing_score,
        "ai_feedback": ai_feedback,
        "created_at": completed.created_at
    }


@router.get("/scores/my")
def get_my_scores(
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student)
):
    return TestService.get_student_scores(db, student.id)