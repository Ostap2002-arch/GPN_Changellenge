from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    database_url: str = "postgresql://postgres:postgres@postgres:5432/device_data"
    redis_url: str = "redis://gpn-redis:6379/0"
    celery_broker_url: str = "redis://gpn-redis:6379/0"
    celery_result_backend: str = "redis://gpn-redis:6379/0"
    api_port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
