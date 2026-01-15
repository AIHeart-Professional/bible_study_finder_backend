"""
Configuration file for Bible Study Finder Backend

This file contains configuration values for the backend including API keys,
database settings, and environment-specific configurations.

WARNING: This is a temporary solution for development.
For production, these values should be:
- Loaded from environment variables (using python-dotenv or similar)
- Stored securely (e.g., using Kubernetes secrets, OpenShift secrets)
- Managed via CI/CD pipelines

DO NOT commit sensitive data to version control.
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    # Environment
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:4200,http://localhost:5173,http://localhost:58080"
    ).split(",")
    
    PRODUCTION_ALLOWED_ORIGINS: List[str] = os.getenv(
        "PRODUCTION_ALLOWED_ORIGINS",
        "https://yourdomain.com"
    ).split(",")
    
    # API Configuration
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Bible Study Finder API")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    
    # Database Configuration (when implemented)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bible_study.db")
    
    # PostgreSQL Configuration
    # Note: If using Supabase or other cloud providers, you can either:
    # 1. Set DATABASE_URL environment variable with full connection string (preferred)
    # 2. Set individual POSTGRES_* environment variables
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "bible_study_finder")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "debug")
    
    # Security (for future use)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # External APIs (for future integration)
    BIBLE_API_KEY: str = os.getenv("BIBLE_API_KEY", "23811ae5496b6f246835a7e387b17d2e")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Cache Settings
    CACHE_EXPIRATION_HOURS: int = int(os.getenv("CACHE_EXPIRATION_HOURS", "24"))
    MAX_CACHE_SIZE_MB: int = int(os.getenv("MAX_CACHE_SIZE_MB", "50"))
    
    # API Timeout Settings (in seconds)
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Pagination Defaults
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.ENVIRONMENT.lower() == "development"
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """Get allowed origins based on environment."""
        if cls.is_production():
            return cls.PRODUCTION_ALLOWED_ORIGINS
        return cls.ALLOWED_ORIGINS


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = False
    ENVIRONMENT = "development"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENVIRONMENT = "production"


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    ENVIRONMENT = "testing"
    DATABASE_URL = "sqlite:///./test_bible_study.db"


# Configuration factory
def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config()

