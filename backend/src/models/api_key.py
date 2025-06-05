"""API Key model for managing external service credentials."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class APIProvider(str, enum.Enum):
    """Supported AI API providers."""
    
    GOOGLE_GEMINI = "google_gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class APIKey(Base):
    """API Key model for managing external AI service credentials."""
    
    __tablename__ = "api_keys"
    
    # User relationship
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    # Basic information
    provider: Mapped[APIProvider] = mapped_column(Enum(APIProvider), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Encrypted API key
    encrypted_api_key: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Configuration
    model_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Usage limits
    daily_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    monthly_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Usage tracking
    daily_usage: Mapped[int] = mapped_column(Integer, default=0)
    monthly_usage: Mapped[int] = mapped_column(Integer, default=0)
    total_usage: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, provider='{self.provider}', name='{self.name}')>"