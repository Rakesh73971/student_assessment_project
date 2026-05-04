"""Database connection and session management."""
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import URL
from sqlalchemy.engine import Connection
from app.core.config import settings
import logging

class Base(DeclarativeBase):
    pass

logger = logging.getLogger(__name__)


SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_hostname,
    port=settings.database_port,
    database=settings.database_name,
)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  
    echo=settings.debug_mode,
    future=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@event.listens_for(Session, "after_begin")
def apply_rls_session_context(session, transaction, connection):
    apply_rls_context(session, connection)


def apply_rls_context(session: Session, connection: Connection | None = None) -> bool:
    
    if not settings.enable_db_rls_context:
        return False
    connection = connection or session.connection()
    if connection.dialect.name != "postgresql":
        return False
    user_id = session.info.get("current_user_id")
    user_role = session.info.get("current_user_role")
    if not user_id or not user_role:
        return False
    connection.execute(text("SELECT set_config('app.current_user_id', :uid, true)"), {"uid": user_id})
    connection.execute(
        text("SELECT set_config('app.current_user_role', :role, true)"),
        {"role": user_role},
    )
    return True


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
