from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models.user import User, UserRole
from app.models.student import Student
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        full_name: str = None,
        role: UserRole = UserRole.STUDENT
    ) -> User:
        email = email.lower()
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        password_hash = hash_password(password)

        try:
            user = User(
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                role=role,
                is_active=True,
            )

            db.add(user)
            db.flush()  
            if role == UserRole.STUDENT:
                student = Student(user_id=user.id)
                db.add(student)

            db.commit()
            db.refresh(user)

            logger.info(f"User registered successfully: {email}")

            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User registration failed"
            )

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> User:
        
        email = email.lower()

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        return user

    @staticmethod
    def create_token(user: User) -> dict:
        token_data = {
            "sub": user.id  
        }
        token = create_access_token(data=token_data)
        return {
            "access_token": token,
            "token_type": "bearer"
        }