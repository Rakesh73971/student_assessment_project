from fastapi import status


def test_get_my_profile(client, test_token, test_user, db):
    """Test getting own student profile."""
    client.headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/v1/students/me")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user_id"] == test_user.id


def test_update_my_profile(client, test_token):
    client.headers = {"Authorization": f"Bearer {test_token}"}
    response = client.put(
        "/api/v1/students/me",
        json={
            "grade_level": "10th",
            "school_name": "Test School",
            "bio": "I am a test student"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["grade_level"] == "10th"
    assert response.json()["school_name"] == "Test School"


def test_get_student_profile(client, test_token, test_user):
    
    client.headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get(f"/api/v1/students/{test_user.id}")
    


def test_list_cohort_students_unauthorized(client, test_token):
    client.headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/v1/students/cohort/1")
    
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_cohort_students_authorized(client, instructor_token):
    client.headers = {"Authorization": f"Bearer {instructor_token}"}
    response = client.get("/api/v1/students/cohort/1")
    
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
