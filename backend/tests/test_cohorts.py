"""Cohort endpoint tests."""
from fastapi import status

from app.models.student import Student


def test_instructor_can_manage_cohort_students(client, instructor_token, test_user, db):
    """Test cohort create/list/detail/update/student assignment/delete flow."""
    client.headers = {"Authorization": f"Bearer {instructor_token}"}

    create_response = client.post(
        "/api/v1/cohorts/",
        json={"name": "Beta Cohort", "description": "Pilot students"}
    )
    assert create_response.status_code == status.HTTP_200_OK
    cohort_id = create_response.json()["id"]

    list_response = client.get("/api/v1/cohorts/")
    assert list_response.status_code == status.HTTP_200_OK
    assert any(c["id"] == cohort_id for c in list_response.json())

    update_response = client.put(
        f"/api/v1/cohorts/{cohort_id}",
        json={"name": "Beta Cohort Updated"}
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["name"] == "Beta Cohort Updated"

    student = db.query(Student).filter(Student.user_id == test_user.id).first()

    add_response = client.post(f"/api/v1/cohorts/{cohort_id}/students/{student.id}")
    assert add_response.status_code == status.HTTP_204_NO_CONTENT

    detail_response = client.get(f"/api/v1/cohorts/{cohort_id}")
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.json()["students_count"] == 1
    assert detail_response.json()["students"][0]["id"] == student.id

    remove_response = client.delete(f"/api/v1/cohorts/{cohort_id}/students/{student.id}")
    assert remove_response.status_code == status.HTTP_204_NO_CONTENT

    delete_response = client.delete(f"/api/v1/cohorts/{cohort_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT


def test_student_cannot_create_cohort(client, test_token):
    """Test that students cannot create cohorts."""
    client.headers = {"Authorization": f"Bearer {test_token}"}

    response = client.post(
        "/api/v1/cohorts/",
        json={"name": "Unauthorized Cohort"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
