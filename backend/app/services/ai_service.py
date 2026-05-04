import logging
import json
import re

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_name = "gemini-2.5-flash"

    def generate_feedback(
        self,
        student_answers: list[dict],
        test_title: str,
        overall_score: float,
    ) -> str:
        try:
            prompt = self._build_feedback_prompt(student_answers, test_title, overall_score)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"You are a helpful teacher giving constructive feedback.\n\n{prompt}",
                config=types.GenerateContentConfig(
                    max_output_tokens=1000,
                    temperature=0.5,
                )
            )
            return (response.text or "").strip() or "Unable to generate feedback at this time."
        except Exception as exc:
            logger.exception("Feedback generation failed: %s", exc)
            return "Unable to generate feedback at this time."

    def evaluate_answer(
        self,
        question_text: str,
        correct_answer: str,
        student_answer: str,
    ) -> bool:
        prompt = f"""
Question: {question_text}
Reference Answer: {correct_answer}
Student Answer: {student_answer}

Grade the student's answer by overall meaning, not by exact word matching.

Rules:
- Mark correct when the student's sentence expresses the same core idea as the reference answer.
- Accept synonyms, changed word order, brief explanations, minor grammar mistakes, and small spelling mistakes.
- Do not require the same vocabulary as the reference answer.
- Mark incorrect only when the meaning is missing, opposite, unrelated, or too vague to prove understanding.
- If one word is wrong but the full sentence still clearly shows the right concept, mark it correct.

Return only valid JSON in this shape:
{{"is_correct": true, "confidence": 0.0, "reason": "short reason"}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=(
                    "You are a fair assessment grader. Grade the answer by "
                    "semantic meaning of the whole response.\n\n"
                    f"{prompt}"
                ),
                config=types.GenerateContentConfig(
                    max_output_tokens=160,
                    temperature=0.1,
                )
            )
            return self._parse_evaluation_response(response.text)
        except Exception as exc:
            logger.exception("Answer evaluation failed: %s", exc)
            return False

    @staticmethod
    def _parse_evaluation_response(response_text: str | None) -> bool:
        text = (response_text or "").strip()
        if not text:
            return False

        json_match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return bool(data.get("is_correct"))
            except (json.JSONDecodeError, TypeError, AttributeError):
                logger.warning("Could not parse AI evaluation JSON: %s", text)

        normalized = text.casefold()
        if re.search(r"\bincorrect\b", normalized):
            return False
        return bool(re.search(r"\bcorrect\b", normalized))

    @staticmethod
    def _build_feedback_prompt(
        student_answers: list[dict],
        test_title: str,
        overall_score: float,
    ) -> str:
        summary = "\n".join(
            f"- {answer['question_text']} -> "
            f"{'Correct' if answer['is_correct'] else 'Wrong'}"
            for answer in student_answers[:10]
        )

        return f"""
Student scored {overall_score}% in "{test_title}".

Results:
{summary}

Give:
- strengths
- weaknesses
- tips
- motivation
"""
