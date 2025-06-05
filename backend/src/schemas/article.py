"""Article schemas for SEO content management."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from ..models.article import ArticleStatus, ContentType


class ArticleBase(BaseModel):
    """Base article schema."""
    title: str
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    content_type: ContentType = ContentType.BLOG_POST
    target_keywords: Optional[List[str]] = None
    featured_image_url: Optional[str] = None


class ArticleCreate(ArticleBase):
    """Schema for creating a new article."""
    project_id: Optional[int] = None


class ArticleUpdate(BaseModel):
    """Schema for updating article information."""
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    content_type: Optional[ContentType] = None
    status: Optional[ArticleStatus] = None
    target_keywords: Optional[List[str]] = None
    featured_image_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class ArticleInDB(ArticleBase):
    """Article schema as stored in database."""
    id: int
    status: ArticleStatus
    word_count: int
    reading_time: int
    ai_generated: bool
    ai_model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    seo_score: Optional[float] = None
    readability_score: Optional[float] = None
    keyword_density: Optional[float] = None
    published_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    external_url: Optional[str] = None
    cms_id: Optional[str] = None
    cms_platform: Optional[str] = None
    page_views: int
    unique_visitors: int
    average_time_on_page: Optional[float] = None
    bounce_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    search_rankings: Optional[dict] = None
    images: Optional[List[str]] = None
    project_id: Optional[int] = None
    author_id: int
    version: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Article(ArticleInDB):
    """Article schema for API responses."""
    pass


class ArticleWithProject(Article):
    """Article schema with project information."""
    project_name: Optional[str] = None


class ArticleGenerate(BaseModel):
    """Schema for AI article generation."""
    topic: str
    keywords: List[str]
    content_type: ContentType = ContentType.BLOG_POST
    target_length: int = 2000
    tone: str = "professional"
    target_audience: Optional[str] = None
    competitor_urls: Optional[List[str]] = None
    ai_provider: Optional[str] = None


class ArticleAnalysis(BaseModel):
    """Schema for article SEO analysis."""
    seo_score: float
    readability_score: float
    keyword_density: dict
    suggestions: List[str]
    issues: List[str]
    strengths: List[str]


class ArticlePublish(BaseModel):
    """Schema for publishing article."""
    cms_platform: str
    publish_immediately: bool = True
    scheduled_at: Optional[datetime] = None