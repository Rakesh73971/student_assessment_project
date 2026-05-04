import pytest
from fastapi import status


def test_register_user(client, db):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_register_existing_email(client, test_user):
    """Test registration with existing email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_invalid_password(client, test_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, test_token):
    """Test getting current user profile."""
    client.headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@example.com"


def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
