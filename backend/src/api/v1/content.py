"""Content Management API endpoints."""

import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.api.deps import get_db, get_current_user
from src.models.article import Article, ArticleStatus, ContentType
from src.models.user import User
from src.schemas.content import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    ArticleAnalytics,
    PublishRequest,
    PublishResponse,
    ArticleSearch
)


router = APIRouter()


def calculate_word_count(content: str) -> int:
    """Calculate word count from content."""
    if not content:
        return 0
    # Simple word count - split by whitespace
    return len(content.split())


def calculate_reading_time(word_count: int) -> int:
    """Calculate reading time in minutes (assumes 200 words per minute)."""
    if word_count == 0:
        return 0
    return max(1, round(word_count / 200))


def calculate_basic_seo_score(article: Article) -> float:
    """Calculate a basic SEO score based on content properties."""
    score = 0.0
    
    # Title length (optimal: 30-60 characters)
    if article.title:
        title_len = len(article.title)
        if 30 <= title_len <= 60:
            score += 20
        elif 20 <= title_len <= 70:
            score += 15
        else:
            score += 5
    
    # Meta description (optimal: 150-160 characters)
    if article.meta_description:
        meta_len = len(article.meta_description)
        if 150 <= meta_len <= 160:
            score += 20
        elif 120 <= meta_len <= 170:
            score += 15
        else:
            score += 10
    
    # Content length (optimal: 1000+ words)
    if article.word_count >= 1000:
        score += 25
    elif article.word_count >= 500:
        score += 20
    elif article.word_count >= 300:
        score += 15
    else:
        score += 5
    
    # Target keywords present
    if article.target_keywords:
        score += 15
    
    # Featured image
    if article.featured_image_url:
        score += 10
    
    # Meta title different from title
    if article.meta_title and article.meta_title != article.title:
        score += 10
    
    return min(100.0, score)


@router.post("/articles/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new article."""
    
    # Calculate word count and reading time
    word_count = calculate_word_count(article.content or "")
    reading_time = calculate_reading_time(word_count)
    
    # Create article instance
    db_article = Article(
        **article.model_dump(exclude_unset=True),
        author_id=current_user.id,
        word_count=word_count,
        reading_time=reading_time
    )
    
    # Calculate basic SEO score
    db_article.seo_score = calculate_basic_seo_score(db_article)
    
    # Generate slug if not provided
    if not db_article.slug and db_article.title:
        slug_base = db_article.title.lower()
        # Simple slug generation - replace spaces with hyphens, remove special chars
        import re
        slug_base = re.sub(r'[^\w\s-]', '', slug_base)
        slug_base = re.sub(r'[-\s]+', '-', slug_base).strip('-')
        db_article.slug = slug_base[:100]  # Limit length
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    return db_article


@router.get("/articles/", response_model=ArticleListResponse)
async def get_articles(
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles to return"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    status: Optional[ArticleStatus] = Query(None, description="Filter by status"),
    content_type: Optional[ContentType] = Query(None, description="Filter by content type"),
    ai_generated: Optional[bool] = Query(None, description="Filter by AI generation"),
    author_id: Optional[int] = Query(None, description="Filter by author"),
    project_id: Optional[int] = Query(None, description="Filter by project"),
    order_by: str = Query("created_at", description="Order by field"),
    order_desc: bool = Query(True, description="Order descending"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get articles list with filtering and pagination."""
    
    query = db.query(Article)
    
    # Apply filters
    filters = []
    
    if search:
        search_filter = or_(
            Article.title.ilike(f"%{search}%"),
            Article.content.ilike(f"%{search}%"),
            Article.meta_description.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if status:
        filters.append(Article.status == status)
    
    if content_type:
        filters.append(Article.content_type == content_type)
    
    if ai_generated is not None:
        filters.append(Article.ai_generated == ai_generated)
    
    if author_id:
        filters.append(Article.author_id == author_id)
    
    if project_id:
        filters.append(Article.project_id == project_id)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Get total count
    total = query.count()
    
    # Apply ordering
    if hasattr(Article, order_by):
        order_column = getattr(Article, order_by)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column)
    
    # Apply pagination
    articles = query.offset(skip).limit(limit).all()
    
    return ArticleListResponse(
        items=articles,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific article by ID."""
    
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    return article


@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing article."""
    
    db_article = db.query(Article).filter(Article.id == article_id).first()
    
    if not db_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if user owns the article (or is admin)
    if db_article.author_id != current_user.id and current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this article"
        )
    
    # Update fields
    update_data = article_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_article, field, value)
    
    # Recalculate word count and reading time if content changed
    if "content" in update_data:
        db_article.word_count = calculate_word_count(db_article.content or "")
        db_article.reading_time = calculate_reading_time(db_article.word_count)
        db_article.seo_score = calculate_basic_seo_score(db_article)
    
    # Update timestamp
    db_article.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_article)
    
    return db_article


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an article."""
    
    db_article = db.query(Article).filter(Article.id == article_id).first()
    
    if not db_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if user owns the article (or is admin)
    if db_article.author_id != current_user.id and current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this article"
        )
    
    db.delete(db_article)
    db.commit()


@router.post("/articles/{article_id}/publish", response_model=PublishResponse)
async def publish_article(
    article_id: int,
    publish_request: Optional[PublishRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish an article."""
    
    db_article = db.query(Article).filter(Article.id == article_id).first()
    
    if not db_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if user owns the article (or is admin)
    if db_article.author_id != current_user.id and current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this article"
        )
    
    # Validate article is ready for publishing
    if not db_article.title or not db_article.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article must have title and content to be published"
        )
    
    # Update publication status
    db_article.status = ArticleStatus.PUBLISHED
    
    if publish_request:
        if publish_request.scheduled_at:
            db_article.scheduled_at = publish_request.scheduled_at
        if publish_request.external_url:
            db_article.external_url = publish_request.external_url
        if publish_request.cms_platform:
            db_article.cms_platform = publish_request.cms_platform
    
    # Set published timestamp if not scheduled
    if not db_article.scheduled_at or db_article.scheduled_at <= datetime.utcnow():
        db_article.published_at = datetime.utcnow()
        message = "Article published successfully"
    else:
        message = f"Article scheduled for publication at {db_article.scheduled_at}"
    
    db_article.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_article)
    
    return PublishResponse(
        id=db_article.id,
        status=db_article.status,
        published_at=db_article.published_at,
        external_url=db_article.external_url,
        message=message
    )


@router.get("/articles/{article_id}/analytics", response_model=ArticleAnalytics)
async def get_article_analytics(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a specific article."""
    
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Parse search rankings JSON if available
    search_rankings_dict = None
    if article.search_rankings:
        try:
            search_rankings_dict = json.loads(article.search_rankings)
        except json.JSONDecodeError:
            search_rankings_dict = None
    
    return ArticleAnalytics(
        article_id=article.id,
        page_views=article.page_views,
        unique_visitors=article.unique_visitors,
        average_time_on_page=article.average_time_on_page,
        bounce_rate=article.bounce_rate,
        conversion_rate=article.conversion_rate,
        seo_score=article.seo_score,
        readability_score=article.readability_score,
        keyword_density=article.keyword_density,
        word_count=article.word_count,
        reading_time=article.reading_time,
        search_rankings=search_rankings_dict
    )


@router.get("/articles/{article_id}/versions", response_model=List[ArticleResponse])
async def get_article_versions(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all versions of an article."""
    
    # Check if base article exists
    base_article = db.query(Article).filter(Article.id == article_id).first()
    if not base_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Get all versions (including the base article and its children)
    versions = db.query(Article).filter(
        or_(
            Article.id == article_id,
            Article.parent_id == article_id
        )
    ).order_by(Article.version.desc()).all()
    
    return versions


@router.post("/articles/{article_id}/duplicate", response_model=ArticleResponse)
async def duplicate_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a duplicate of an article as a draft."""
    
    original_article = db.query(Article).filter(Article.id == article_id).first()
    
    if not original_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Create duplicate
    duplicate_data = {
        "title": f"Copy of {original_article.title}",
        "content": original_article.content,
        "excerpt": original_article.excerpt,
        "meta_title": original_article.meta_title,
        "meta_description": original_article.meta_description,
        "meta_keywords": original_article.meta_keywords,
        "content_type": original_article.content_type,
        "status": ArticleStatus.DRAFT,  # Always start as draft
        "target_keywords": original_article.target_keywords,
        "ai_generated": original_article.ai_generated,
        "ai_model_used": original_article.ai_model_used,
        "generation_prompt": original_article.generation_prompt,
        "featured_image_url": original_article.featured_image_url,
        "images": original_article.images,
        "project_id": original_article.project_id,
        "author_id": current_user.id,
        "word_count": original_article.word_count,
        "reading_time": original_article.reading_time,
        "parent_id": original_article.id,
        "version": original_article.version + 1
    }
    
    duplicate_article = Article(**duplicate_data)
    duplicate_article.seo_score = calculate_basic_seo_score(duplicate_article)
    
    db.add(duplicate_article)
    db.commit()
    db.refresh(duplicate_article)
    
    return duplicate_article