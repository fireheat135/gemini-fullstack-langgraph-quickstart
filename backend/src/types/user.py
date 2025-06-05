"""
User-related type definitions
ユーザー関連の型定義
"""
from typing import TypedDict, Literal, Optional, List
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

# Enums and Literal Types
UserRole = Literal["admin", "editor", "author", "viewer"]
SubscriptionTier = Literal["free", "basic", "premium", "enterprise"]
AuthProvider = Literal["email", "google", "github", "microsoft"]

# Input Types
class UserRegistrationInput(TypedDict):
    """ユーザー登録入力"""
    email: str
    password: str
    display_name: str
    company_name: Optional[str]
    subscription_tier: SubscriptionTier

class UserProfileUpdate(TypedDict):
    """ユーザープロフィール更新"""
    display_name: Optional[str]
    company_name: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    timezone: Optional[str]

# Result Types
@dataclass(frozen=True)
class UserProfile:
    """ユーザープロフィール"""
    id: str
    email: str
    display_name: str
    company_name: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    timezone: str
    role: UserRole
    subscription_tier: SubscriptionTier
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]

@dataclass(frozen=True)
class UserUsageStatistics:
    """ユーザー使用統計"""
    user_id: str
    articles_created: int
    meta_descriptions_generated: int
    images_generated: int
    api_calls_made: int
    storage_used_mb: Decimal
    current_period_start: datetime
    current_period_end: datetime

@dataclass(frozen=True)
class UserSubscriptionDetails:
    """ユーザーサブスクリプション詳細"""
    user_id: str
    tier: SubscriptionTier
    is_active: bool
    renewal_date: Optional[datetime]
    features_enabled: List[str]
    usage_limits: dict[str, int]
    billing_email: Optional[str]