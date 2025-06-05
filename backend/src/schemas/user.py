"""User schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str
    role: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    language: str = "ja"
    timezone: str = "Asia/Tokyo"


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


class User(UserInDB):
    """User schema for API responses."""
    pass


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str