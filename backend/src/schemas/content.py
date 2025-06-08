"""Content management schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from src.models.article import ArticleStatus, ContentType


class ArticleBase(BaseModel):
    """Base article schema."""
    
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    slug: Optional[str] = Field(None, max_length=500, description="URL slug")
    content: Optional[str] = Field(None, description="Article content")
    excerpt: Optional[str] = Field(None, description="Article excerpt")
    
    # SEO metadata
    meta_title: Optional[str] = Field(None, max_length=500, description="SEO title")
    meta_description: Optional[str] = Field(None, max_length=1000, description="SEO description")
    meta_keywords: Optional[str] = Field(None, description="SEO keywords")
    
    # Content properties
    content_type: ContentType = Field(ContentType.BLOG_POST, description="Content type")
    status: ArticleStatus = Field(ArticleStatus.DRAFT, description="Article status")
    
    # Target keywords
    target_keywords: Optional[str] = Field(None, description="Target keywords for SEO")
    
    # AI generation metadata
    ai_generated: bool = Field(False, description="Whether content was AI-generated")
    ai_model_used: Optional[str] = Field(None, max_length=100, description="AI model used")
    generation_prompt: Optional[str] = Field(None, description="Prompt used for generation")
    
    # Publishing
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time")
    
    # External publishing
    external_url: Optional[str] = Field(None, max_length=1000, description="External URL")
    cms_id: Optional[str] = Field(None, max_length=255, description="CMS ID")
    cms_platform: Optional[str] = Field(None, max_length=100, description="CMS platform")
    
    # Media
    featured_image_url: Optional[str] = Field(None, max_length=1000, description="Featured image URL")
    images: Optional[str] = Field(None, description="Additional images (JSON)")
    
    # Project relationship
    project_id: Optional[int] = Field(None, description="Associated project ID")


class ArticleCreate(ArticleBase):
    """Schema for creating articles."""
    pass


class ArticleUpdate(BaseModel):
    """Schema for updating articles."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    slug: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    excerpt: Optional[str] = None
    
    meta_title: Optional[str] = Field(None, max_length=500)
    meta_description: Optional[str] = Field(None, max_length=1000)
    meta_keywords: Optional[str] = None
    
    content_type: Optional[ContentType] = None
    status: Optional[ArticleStatus] = None
    
    target_keywords: Optional[str] = None
    
    ai_generated: Optional[bool] = None
    ai_model_used: Optional[str] = Field(None, max_length=100)
    generation_prompt: Optional[str] = None
    
    scheduled_at: Optional[datetime] = None
    
    external_url: Optional[str] = Field(None, max_length=1000)
    cms_id: Optional[str] = Field(None, max_length=255)
    cms_platform: Optional[str] = Field(None, max_length=100)
    
    featured_image_url: Optional[str] = Field(None, max_length=1000)
    images: Optional[str] = None
    
    project_id: Optional[int] = None


class ArticleResponse(ArticleBase):
    """Schema for article responses."""
    
    id: int
    word_count: int
    reading_time: int
    
    # SEO scores
    seo_score: Optional[float] = None
    readability_score: Optional[float] = None
    keyword_density: Optional[float] = None
    
    # Publishing information
    published_at: Optional[datetime] = None
    
    # Analytics
    page_views: int = 0
    unique_visitors: int = 0
    average_time_on_page: Optional[float] = None
    bounce_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    
    # Search rankings
    search_rankings: Optional[str] = None
    
    # Author
    author_id: int
    
    # Version control
    version: int = 1
    parent_id: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Schema for paginated article lists."""
    
    items: List[ArticleResponse]
    total: int
    skip: int
    limit: int


class ArticleAnalytics(BaseModel):
    """Schema for article analytics."""
    
    article_id: int
    page_views: int
    unique_visitors: int
    average_time_on_page: Optional[float] = None
    bounce_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    seo_score: Optional[float] = None
    readability_score: Optional[float] = None
    keyword_density: Optional[float] = None
    word_count: int
    reading_time: int
    search_rankings: Optional[dict] = None
    
    class Config:
        from_attributes = True


class PublishRequest(BaseModel):
    """Schema for publishing articles."""
    
    scheduled_at: Optional[datetime] = Field(None, description="Schedule publication time")
    external_url: Optional[str] = Field(None, max_length=1000, description="External publication URL")
    cms_platform: Optional[str] = Field(None, max_length=100, description="CMS platform")


class PublishResponse(BaseModel):
    """Schema for publish response."""
    
    id: int
    status: ArticleStatus
    published_at: Optional[datetime]
    external_url: Optional[str] = None
    message: str
    
    class Config:
        from_attributes = True


class ArticleSearch(BaseModel):
    """Schema for article search parameters."""
    
    search: Optional[str] = Field(None, description="Search term for title/content")
    status: Optional[ArticleStatus] = Field(None, description="Filter by status")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    author_id: Optional[int] = Field(None, description="Filter by author")
    project_id: Optional[int] = Field(None, description="Filter by project")
    ai_generated: Optional[bool] = Field(None, description="Filter AI-generated content")
    created_from: Optional[datetime] = Field(None, description="Created after date")
    created_to: Optional[datetime] = Field(None, description="Created before date")
    published_from: Optional[datetime] = Field(None, description="Published after date")
    published_to: Optional[datetime] = Field(None, description="Published before date")
    min_word_count: Optional[int] = Field(None, ge=0, description="Minimum word count")
    max_word_count: Optional[int] = Field(None, ge=0, description="Maximum word count")
    min_seo_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum SEO score")
    
    @field_validator('max_word_count')
    @classmethod
    def validate_word_count_range(cls, v, info):
        """Validate word count range."""
        if v is not None and info.data.get('min_word_count') is not None:
            if v < info.data['min_word_count']:
                raise ValueError('max_word_count must be greater than min_word_count')
        return v