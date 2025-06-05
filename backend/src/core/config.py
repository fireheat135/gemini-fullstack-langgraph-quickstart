"""Configuration settings for the SEO Agent Platform."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "SEO Agent Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost/seo_agent",
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = Field(default=False, description="Log SQL queries")
    
    # Redis (for caching and task queue)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT tokens"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    
    # Encryption key for API keys
    ENCRYPTION_KEY: str = Field(
        default="",
        description="Encryption key for storing API keys"
    )
    
    # AI Service API Keys
    GOOGLE_GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key"
    )
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None,
        description="Anthropic Claude API key"
    )
    
    # External APIs
    GOOGLE_ANALYTICS_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="Google Analytics client ID"
    )
    GOOGLE_ANALYTICS_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="Google Analytics client secret"
    )
    GOOGLE_SEARCH_CONSOLE_CLIENT_ID: Optional[str] = Field(
        default=None,
        description="Google Search Console client ID"
    )
    GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET: Optional[str] = Field(
        default=None,
        description="Google Search Console client secret"
    )
    
    # Email settings (for notifications)
    SMTP_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    SMTP_PORT: Optional[int] = Field(default=587, description="SMTP port")
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    EMAILS_FROM_EMAIL: Optional[str] = Field(
        default=None,
        description="Email address to send from"
    )
    EMAILS_FROM_NAME: Optional[str] = Field(
        default=None,
        description="Name to send emails from"
    )
    
    # Celery (task queue)
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/1",
        description="Celery result backend URL"
    )
    
    # File storage
    UPLOAD_DIR: str = Field(
        default="uploads",
        description="Directory for file uploads"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum upload file size in bytes"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Number of requests per minute"
    )
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )
    
    # LangGraph configuration
    LANGGRAPH_API_URL: Optional[str] = Field(
        default=None,
        description="LangGraph API URL"
    )
    LANGGRAPH_API_KEY: Optional[str] = Field(
        default=None,
        description="LangGraph API key"
    )
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings