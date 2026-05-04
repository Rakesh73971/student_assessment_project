from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db, apply_rls_context
from app.core.security import decode_token
from app.models.user import User, UserRole

import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


# ==================== TOKEN ====================

def get_token_from_header(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# ==================== AUTH USER ====================

def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == int(user_id)).first()

        if not user:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive"
            )

        
        db.info["current_user_id"] = str(user.id)
        db.info["current_user_role"] = user.role.value
        apply_rls_context(db)

        return user

    except Exception as e:
        logger.warning(f"Auth failed: {str(e)}")
        raise credentials_exception


# ==================== ROLE BASED ====================

def get_current_student(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    from app.models.student import Student

    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students only"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    return student


def get_current_instructor(
    current_user: User = Depends(get_current_user)
) -> User:

    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructors/Admins only"
        )

    return current_user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )

    return current_user
