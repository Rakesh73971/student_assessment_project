from fastapi import status


def test_admin_can_list_users_and_view_stats(
    client,
    admin_token,
    test_user,
    test_instructor
):
    """Test core admin visibility endpoints."""
    client.headers = {"Authorization": f"Bearer {admin_token}"}

    users_response = client.get("/api/v1/admin/users")
    assert users_response.status_code == status.HTTP_200_OK
    assert users_response.json()["total"] >= 3

    overview_response = client.get("/api/v1/admin/stats/overview")
    assert overview_response.status_code == status.HTTP_200_OK
    assert overview_response.json()["total_students"] >= 1
    assert overview_response.json()["total_instructors"] >= 1

    student_stats_response = client.get("/api/v1/admin/stats/students")
    assert student_stats_response.status_code == status.HTTP_200_OK
    assert student_stats_response.json()["total_students"] >= 1


def test_admin_can_update_user_status(client, admin_token, test_user):
    """Test admin user status updates."""
    client.headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.put(
        f"/api/v1/admin/users/{test_user.id}/status",
        json={"is_active": False}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is False


def test_non_admin_cannot_access_admin_routes(client, instructor_token):
    """Test that instructors cannot access admin-only routes."""
    client.headers = {"Authorization": f"Bearer {instructor_token}"}

    response = client.get("/api/v1/admin/users")

    assert response.status_code == status.HTTP_403_FORBIDDEN
