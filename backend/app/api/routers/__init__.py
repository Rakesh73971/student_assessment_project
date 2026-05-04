from app.api.routers.auth_routes import router as auth_router
from app.api.routers.student_routes import router as student_router
from app.api.routers.test_routes import router as test_router

__all__ = ["auth_router", "student_router", "test_router"]
