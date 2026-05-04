from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.api.deps import get_db, get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    UserUpdateProfile
)
from app.services.auth_services import AuthService
from app.models.user import User, UserRole
from app.core.security import hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# =========================
# REGISTER
# =========================

@router.post("/register", response_model=Token)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user."""

    try:
        user = AuthService.register_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role or UserRole.STUDENT,
        )

        return AuthService.create_token(user)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


# =========================
# LOGIN
# =========================

@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):

    try:
        user = AuthService.authenticate_user(
            db=db,
            email=credentials.email,
            password=credentials.password
        )

        return AuthService.create_token(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


# =========================
# CURRENT USER
# =========================

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user."""
    return current_user


# =========================
# UPDATE PROFILE
# =========================

@router.put("/me/profile", response_model=UserResponse)
def update_user_profile(
    profile_data: UserUpdateProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""

    try:
        if profile_data.full_name is not None:
            current_user.full_name = profile_data.full_name

        if profile_data.bio is not None:
            current_user.bio = profile_data.bio

        if profile_data.password:
            if len(profile_data.password) < 8:
                raise HTTPException(
                    status_code=400,
                    detail="Password must be at least 8 characters"
                )
            current_user.password_hash = hash_password(profile_data.password)

        db.commit()
        db.refresh(current_user)

        logger.info(f"User {current_user.id} updated profile")

        return current_user

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update profile"
        )