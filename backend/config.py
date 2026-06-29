"""
Application Configuration
Uses pydantic-settings for environment-based configuration.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "S3OS - Academic Operating System"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./s3os.db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Scheduling
    SEMESTER_START_DATE: str = "2025-07-14"
    SEMESTER_END_DATE: str = "2025-11-10"
    AMCAT_START_DATE: str = "2025-08-15"
    AMCAT_END_DATE: str = "2025-09-15"
    EXAM_START_DATE: str = "2025-11-01"
    
    # Fixed Daily Schedule
    SLEEP_START: str = "23:30"
    SLEEP_END: str = "07:00"
    COLLEGE_START: str = "09:30"
    COLLEGE_END: str = "16:30"
    GYM_START: str = "17:30"
    GYM_END: str = "19:00"
    DINNER_START: str = "20:15"
    DINNER_END: str = "20:45"
    
    # Study Time
    MORNING_REVISION_START: str = "07:15"
    MORNING_REVISION_END: str = "08:00"
    EVENING_STUDY_START: str = "19:30"
    NIGHT_STUDY_START: str = "20:45"
    NIGHT_STUDY_END: str = "23:30"
    
    # Total available study hours per week
    TOTAL_AVAILABLE_STUDY_HOURS: float = 30.0
    AMCAT_TARGET_HOURS_PER_WEEK: float = 15.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
