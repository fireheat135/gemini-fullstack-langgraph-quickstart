"""API Key schemas for managing external service credentials."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.api_key import APIProvider


class APIKeyBase(BaseModel):
    """Base API key schema."""
    provider: APIProvider
    name: str
    model_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None


class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key."""
    api_key: str  # This will be encrypted before storage


class APIKeyUpdate(BaseModel):
    """Schema for updating API key information."""
    api_key: Optional[str] = None
    name: Optional[str] = None
    model_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    is_active: Optional[bool] = None


class APIKeyInDB(APIKeyBase):
    """API key schema as stored in database."""
    id: int
    user_id: int
    daily_usage: int
    monthly_usage: int
    total_usage: int
    is_active: bool
    is_verified: bool
    last_used_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APIKeyResponse(APIKeyInDB):
    """API key schema for API responses (without encrypted key)."""
    pass


class APIKeyWithUsage(APIKeyResponse):
    """API key schema with usage statistics."""
    usage_percentage_daily: Optional[float] = None
    usage_percentage_monthly: Optional[float] = None
    remaining_daily: Optional[int] = None
    remaining_monthly: Optional[int] = None


class APIKeyTest(BaseModel):
    """Schema for API key test results."""
    success: bool
    error: Optional[str] = None
    response_time: Optional[float] = None
    model_info: Optional[dict] = None


class APIKeyUsageUpdate(BaseModel):
    """Schema for updating API key usage."""
    tokens_used: int