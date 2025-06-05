"""Article model for managing SEO content."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ArticleStatus(str, enum.Enum):
    """Article status options."""
    
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentType(str, enum.Enum):
    """Content type options."""
    
    BLOG_POST = "blog_post"
    LANDING_PAGE = "landing_page"
    PRODUCT_DESCRIPTION = "product_description"
    FAQ = "faq"
    GUIDE = "guide"
    NEWS = "news"


class Article(Base):
    """Article model for SEO content management."""
    
    # Basic information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # SEO metadata
    meta_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    meta_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Content properties
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType), default=ContentType.BLOG_POST)
    status: Mapped[ArticleStatus] = mapped_column(Enum(ArticleStatus), default=ArticleStatus.DRAFT)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    reading_time: Mapped[int] = mapped_column(Integer, default=0)  # minutes
    
    # Target keywords (JSON stored as string)
    target_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # AI generation metadata
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    generation_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # SEO scores
    seo_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    readability_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    keyword_density: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Publishing information
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # External publishing
    external_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    cms_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cms_platform: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Analytics
    page_views: Mapped[int] = mapped_column(Integer, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
    average_time_on_page: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bounce_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    conversion_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Search rankings (JSON stored as string)
    search_rankings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Media
    featured_image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    
    # Project relationship
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("project.id"), nullable=True)
    
    # Author relationship
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("article.id"), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="articles")
    author = relationship("User")
    parent = relationship("Article", remote_side=[id])
    children = relationship("Article")
    
    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title[:50]}...', status='{self.status}')>"