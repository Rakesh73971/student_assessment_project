
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_hostname: str
    database_port: int = 5432
    database_password: str
    database_name: str
    database_username: str
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    google_api_key: str
    
    debug_mode: bool = False
    environment: str = "development"
    app_name: str = "Student Assessment API"
    app_version: str = "1.0.0"
    request_slow_ms: int = 800
    enable_db_rls_context: bool = True
    
    
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
