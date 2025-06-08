"""User model for authentication and authorization."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserRole(str, Enum):
    """User roles for role-based access control."""
    ADMIN = "admin"
    MANAGER = "manager"
    WRITER = "writer"
    REVIEWER = "reviewer"


class User(Base):
    """User model for the SEO Agent platform."""
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.WRITER, nullable=False)
    
    # Status flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Profile fields
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Job title/role
    
    # Preferences
    language: Mapped[str] = mapped_column(String(10), default="ja")
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Tokyo")
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # OAuth fields
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Activity tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="author")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}', role='{self.user_role}')>"
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Check if user has required permission level."""
        role_hierarchy = {
            UserRole.ADMIN: 4,
            UserRole.MANAGER: 3,
            UserRole.WRITER: 2,
            UserRole.REVIEWER: 1
        }
        return role_hierarchy.get(self.user_role, 0) >= role_hierarchy.get(required_role, 0)