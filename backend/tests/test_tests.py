from fastapi import status


def test_create_test(client, instructor_token):
    client.headers = {"Authorization": f"Bearer {instructor_token}"}
    response = client.post(
        "/api/v1/tests/",
        json={
            "title": "Math Quiz",
            "description": "Basic algebra",
            "subject": "Mathematics",
            "duration_minutes": 30,
            "passing_score": 70,
            "test_type": "practice",
            "questions": [],
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_get_test(client, instructor_token):
    client.headers = {"Authorization": f"Bearer {instructor_token}"}
    response = client.get("/api/v1/tests/999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_my_scores(client, test_token):
    client.headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/v1/tests/scores/my")
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_get_my_scores_unauthorized(client):
    response = client.get("/api/v1/tests/scores/my")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
