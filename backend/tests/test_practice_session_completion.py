from fastapi import status


def test_student_can_complete_practice_session_and_receive_score(
    client,
    instructor_token,
    test_token,
    monkeypatch
):
    from app.api.routers import test_routes

    monkeypatch.setattr(
        test_routes.ai_service,
        "generate_feedback",
        lambda **kwargs: "Keep practicing the missed concepts."
    )

    client.headers = {"Authorization": f"Bearer {instructor_token}"}
    create_response = client.post(
        "/api/v1/tests/",
        json={
            "title": "Completion Flow Quiz",
            "description": "Checks score calculation",
            "subject": "Math",
            "duration_minutes": 20,
            "passing_score": 70,
            "test_type": "practice",
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "question_type": "short_answer",
                    "correct_answer": "4",
                    "points": 5,
                    "order": 1
                },
                {
                    "question_text": "What is 3 + 3?",
                    "question_type": "short_answer",
                    "correct_answer": "6",
                    "points": 5,
                    "order": 2
                }
            ]
        }
    )
    assert create_response.status_code == status.HTTP_200_OK
    test_id = create_response.json()["id"]

    detail_response = client.get(f"/api/v1/tests/{test_id}")
    assert detail_response.status_code == status.HTTP_200_OK
    questions = detail_response.json()["questions"]

    client.headers = {"Authorization": f"Bearer {test_token}"}
    start_response = client.post(
        "/api/v1/tests/sessions/start",
        json={"test_id": test_id}
    )
    assert start_response.status_code == status.HTTP_200_OK
    session_id = start_response.json()["session_id"]

    first_answer = client.post(
        f"/api/v1/tests/sessions/{session_id}/submit-response",
        json={"question_id": questions[0]["id"], "answer_text": "4"}
    )
    assert first_answer.status_code == status.HTTP_200_OK

    second_answer = client.post(
        f"/api/v1/tests/sessions/{session_id}/submit-response",
        json={"question_id": questions[1]["id"], "answer_text": "7"}
    )
    assert second_answer.status_code == status.HTTP_200_OK

    complete_response = client.post(f"/api/v1/tests/sessions/{session_id}/complete")
    assert complete_response.status_code == status.HTTP_200_OK
    assert complete_response.json()["score"] == 50
    assert complete_response.json()["passed"] is False
    assert complete_response.json()["ai_feedback"] == "Keep practicing the missed concepts."

    scores_response = client.get("/api/v1/tests/scores/my")
    assert scores_response.status_code == status.HTTP_200_OK
    assert len(scores_response.json()) == 1
    assert scores_response.json()[0]["score"] == 50
    assert scores_response.json()[0]["session_id"] == session_id


def test_answer_scoring_ignores_case_and_extra_whitespace(
    client,
    instructor_token,
    test_token,
    monkeypatch,
):
    from app.api.routers import test_routes

    monkeypatch.setattr(
        test_routes.ai_service,
        "generate_feedback",
        lambda **kwargs: "OK",
    )

    client.headers = {"Authorization": f"Bearer {instructor_token}"}
    create_response = client.post(
        "/api/v1/tests/",
        json={
            "title": "Normalization Quiz",
            "description": "",
            "subject": "Math",
            "duration_minutes": 10,
            "passing_score": 70,
            "test_type": "practice",
            "questions": [
                {
                    "question_text": "Capital of France?",
                    "question_type": "short_answer",
                    "correct_answer": "Paris",
                    "points": 10,
                    "order": 1,
                },
                {
                    "question_text": "Say hello",
                    "question_type": "short_answer",
                    "correct_answer": "hello world",
                    "points": 10,
                    "order": 2,
                },
            ],
        },
    )
    assert create_response.status_code == status.HTTP_200_OK
    test_id = create_response.json()["id"]
    questions = client.get(f"/api/v1/tests/{test_id}").json()["questions"]

    client.headers = {"Authorization": f"Bearer {test_token}"}
    session_id = client.post(
        "/api/v1/tests/sessions/start",
        json={"test_id": test_id},
    ).json()["session_id"]

    client.post(
        f"/api/v1/tests/sessions/{session_id}/submit-response",
        json={"question_id": questions[0]["id"], "answer_text": "  pARIS "},
    )
    client.post(
        f"/api/v1/tests/sessions/{session_id}/submit-response",
        json={"question_id": questions[1]["id"], "answer_text": "HELLO   WORLD"},
    )

    complete_response = client.post(
        f"/api/v1/tests/sessions/{session_id}/complete",
    )
    assert complete_response.status_code == status.HTTP_200_OK
    assert complete_response.json()["score"] == 100
    assert complete_response.json()["passed"] is True