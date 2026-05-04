from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routers import auth_router, student_router, test_router
from app.api.routers.cohort_routes import router as cohort_router
from app.api.routers.admin_routes import router as admin_router

import logging
import time

# ==================== LOGGING ====================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ==================== APP FACTORY ====================

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Student Assessment Platform API",
        version=settings.app_version,
        debug=settings.debug_mode
    )

    # ==================== MIDDLEWARE ====================

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_timing_middleware(request: Request, call_next):
        """Record request latency and log slow responses."""
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
        if elapsed_ms >= settings.request_slow_ms:
            logger.warning(
                "Slow request: %s %s took %.2fms",
                request.method,
                request.url.path,
                elapsed_ms,
            )
        return response

    # ==================== STARTUP ====================

    @app.on_event("startup")
    def startup():
        """Run on app startup."""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables ensured")
        except Exception as e:
            logger.error(f"DB init error: {e}")


    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version
        }

    @app.get("/")
    def root():
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs"
        }

    # ==================== ROUTERS ====================

    app.include_router(auth_router)
    app.include_router(student_router)
    app.include_router(test_router)
    app.include_router(cohort_router)
    app.include_router(admin_router)

    # ==================== GLOBAL EXCEPTION ====================

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"{request.method} {request.url} - {exc}")

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app


# Create app instance
app = create_app()


# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode
    )