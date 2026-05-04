from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
import logging
import re
import unicodedata
from typing import List

from app.models.test import Test
from app.models.practice_session import PracticeSession
from app.models.response import Response
from app.models.score import Score
from app.models.question import Question
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


def _normalize_answer_for_scoring(text: str | None) -> str:
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text))
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s.casefold()


class TestService:

    @staticmethod
    def create_test(
        db: Session,
        title: str,
        description: str,
        cohort_id: int,
        created_by: int,
        test_type: str = "practice",
        subject: str = None,
        duration_minutes: int = None,
        passing_score: int = 70
    ) -> Test:
        try:
            test = Test(
                title=title,
                description=description,
                cohort_id=cohort_id,
                created_by=created_by,
                test_type=test_type,
                subject=subject,
                duration_minutes=duration_minutes,
                passing_score=passing_score
            )

            db.add(test)
            db.commit()
            db.refresh(test)

            logger.info(f"Test created: {test.id}")
            return test

        except Exception as e:
            db.rollback()
            logger.error(f"Create test error: {e}")
            raise HTTPException(500, "Failed to create test")

    @staticmethod
    def get_test(db: Session, test_id: int) -> Test:
        test = db.query(Test).filter(Test.id == test_id).first()

        if not test:
            raise HTTPException(404, "Test not found")

        return test

    @staticmethod
    def add_question_to_test(
        db: Session,
        test_id: int,
        question_text: str,
        question_type: str,
        correct_answer: str,
        options: str = None,
        explanation: str = None,
        points: int = 1,
        order: int = None
    ) -> Question:

        TestService.get_test(db, test_id)

        try:
            if order is None:
                order = db.query(Question).filter(
                    Question.test_id == test_id
                ).count() + 1

            question = Question(
                test_id=test_id,
                question_text=question_text,
                question_type=question_type,
                correct_answer=correct_answer,
                options=options,
                explanation=explanation,
                points=points,
                order=order
            )

            db.add(question)
            db.commit()
            db.refresh(question)

            return question

        except Exception as e:
            db.rollback()
            logger.error(f"Add question error: {e}")
            raise HTTPException(500, "Failed to add question")

    @staticmethod
    def start_practice_session(
        db: Session,
        student_id: int,
        test_id: int
    ) -> PracticeSession:

        TestService.get_test(db, test_id)

        session = db.query(PracticeSession).filter(
            PracticeSession.student_id == student_id,
            PracticeSession.test_id == test_id,
            PracticeSession.completed_at.is_(None)
        ).first()

        if session:
            return session

        try:
            session = PracticeSession(
                student_id=student_id,
                test_id=test_id
            )

            db.add(session)
            db.commit()
            db.refresh(session)

            return session

        except Exception as e:
            db.rollback()
            logger.error(f"Session start error: {e}")
            raise HTTPException(500, "Failed to start session")

    @staticmethod
    def submit_response(
        db: Session,
        session_id: int,
        question_id: int,
        student_id: int,
        answer_text: str
    ) -> Response:

        session = db.query(PracticeSession).filter(
            PracticeSession.id == session_id
        ).first()

        if not session:
            raise HTTPException(404, "Session not found")

        if session.student_id != student_id:
            raise HTTPException(403, "Not authorized")

        question = db.query(Question).filter(
            Question.id == question_id
        ).first()

        if not question:
            raise HTTPException(404, "Question not found")

        try:
            existing = db.query(Response).filter(
                Response.session_id == session_id,
                Response.question_id == question_id
            ).first()

            if existing:
                existing.answer_text = answer_text
                db.commit()
                db.refresh(existing)
                return existing

            response = Response(
                session_id=session_id,
                question_id=question_id,
                student_id=student_id,
                answer_text=answer_text
            )

            db.add(response)
            db.commit()
            db.refresh(response)

            return response

        except Exception as e:
            db.rollback()
            logger.error(f"Submit response error: {e}")
            raise HTTPException(500, "Failed to submit response")

    @staticmethod
    def complete_session(
        db: Session,
        session_id: int
    ) -> PracticeSession:

        session = db.query(PracticeSession).filter(
            PracticeSession.id == session_id
        ).first()

        if not session:
            raise HTTPException(404, "Session not found")

        if session.completed_at is not None:
            return session

        try:
            responses = db.query(Response).filter(
                Response.session_id == session_id
            ).all()

            total_points = 0
            earned_points = 0

            ai_service = AIService()

            for r in responses:
                q = r.question
                total_points += q.points

                student_ans = _normalize_answer_for_scoring(r.answer_text)
                correct = _normalize_answer_for_scoring(q.correct_answer)
                
                is_correct = False
                if student_ans == correct:
                    is_correct = True
                else:
                    # Fallback to AI semantic evaluation
                    is_correct = ai_service.evaluate_answer(
                        question_text=q.question_text,
                        correct_answer=q.correct_answer,
                        student_answer=r.answer_text
                    )

                if is_correct:
                    r.is_correct = True
                    r.points_earned = q.points
                    earned_points += q.points
                else:
                    r.is_correct = False
                    r.points_earned = 0

            score_percentage = (earned_points / total_points * 100) if total_points else 0

            session.completed_at = datetime.now(timezone.utc)
            session.score = score_percentage

            # Score record
            attempt = db.query(Score).filter(
                Score.student_id == session.student_id,
                Score.test_id == session.test_id
            ).count() + 1

            score = Score(
                student_id=session.student_id,
                test_id=session.test_id,
                session_id=session.id,
                score=score_percentage,
                max_points=total_points,
                earned_points=earned_points,
                is_passed=score_percentage >= session.test.passing_score,
                attempt_number=attempt
            )

            db.add(score)
            db.commit()
            db.refresh(session)

            return session

        except Exception as e:
            db.rollback()
            logger.error(f"Complete session error: {e}")
            raise HTTPException(500, "Failed to complete session")

    @staticmethod
    def get_student_scores(db: Session, student_id: int) -> List[Score]:
        return db.query(Score).filter(
            Score.student_id == student_id
        ).all()
