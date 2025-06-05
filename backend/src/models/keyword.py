"""Keyword model for SEO research and tracking."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class KeywordStatus(str, enum.Enum):
    """Keyword tracking status."""
    
    RESEARCHING = "researching"
    TARGETING = "targeting"
    RANKED = "ranked"
    ABANDONED = "abandoned"


class KeywordDifficulty(str, enum.Enum):
    """Keyword difficulty levels."""
    
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class Keyword(Base):
    """Keyword model for SEO research and ranking tracking."""
    
    # Basic information
    keyword: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), default="ja")
    country: Mapped[str] = mapped_column(String(10), default="JP")
    
    # SEO metrics
    search_volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    competition_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cpc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Cost per click
    difficulty: Mapped[Optional[KeywordDifficulty]] = mapped_column(Enum(KeywordDifficulty), nullable=True)
    
    # Tracking information
    status: Mapped[KeywordStatus] = mapped_column(Enum(KeywordStatus), default=KeywordStatus.RESEARCHING)
    target_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    best_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # SERP features (JSON stored as string)
    serp_features: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Related keywords
    related_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    long_tail_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    
    # Trend data
    trend_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON time series data
    seasonality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Performance tracking
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    ctr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Click-through rate
    
    # Content association
    target_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    content_gap: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Last update tracking
    last_rank_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_volume_update: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Project relationship
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("project.id"), nullable=True)
    
    # User who added this keyword
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    # Tags and categorization
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # informational, commercial, navigational, transactional
    
    # Notes and custom data
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON for additional metadata
    
    # Relationships
    project = relationship("Project", back_populates="keywords")
    user = relationship("User")
    
    def __repr__(self) -> str:
        return f"<Keyword(id={self.id}, keyword='{self.keyword}', status='{self.status}')>"