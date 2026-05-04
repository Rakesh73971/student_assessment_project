from app.services.ai_service import AIService


def test_parse_evaluation_response_accepts_json_true():
    assert AIService._parse_evaluation_response(
        '{"is_correct": true, "confidence": 0.93, "reason": "same meaning"}'
    )


def test_parse_evaluation_response_rejects_json_false():
    assert not AIService._parse_evaluation_response(
        '{"is_correct": false, "confidence": 0.88, "reason": "opposite meaning"}'
    )


def test_parse_evaluation_response_does_not_treat_incorrect_as_correct():
    assert not AIService._parse_evaluation_response("INCORRECT")


def test_parse_evaluation_response_supports_legacy_correct_text():
    assert AIService._parse_evaluation_response("CORRECT")
