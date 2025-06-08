"""User schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from ..models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str
    username: Optional[str] = None
    user_role: UserRole = UserRole.WRITER
    role: Optional[str] = None  # Job title
    company: Optional[str] = None
    bio: Optional[str] = None
    language: str = "ja"
    timezone: str = "Asia/Tokyo"
    notification_enabled: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


class UserInDB(UserBase):
    """User schema as stored in database."""
    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """User schema for API responses."""
    pass


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str