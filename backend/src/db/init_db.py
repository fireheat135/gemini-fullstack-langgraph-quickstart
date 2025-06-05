"""Initialize database with sample data."""

from sqlalchemy.orm import Session

from ..models.user import User
from ..models.project import Project, ProjectStatus
from ..models.api_key import APIKey, APIProvider
from ..core.security import get_password_hash


def init_db(db: Session) -> None:
    """Initialize database with sample data."""
    
    # Check if we already have users
    user = db.query(User).first()
    if user:
        return
    
    # Create a sample user
    sample_user = User(
        email="admin@seo-agent.com",
        name="Admin User",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
        is_verified=True,
        role="admin",
        company="SEO Agent Platform",
        bio="Platform administrator",
    )
    db.add(sample_user)
    db.commit()
    db.refresh(sample_user)
    
    # Create a sample project
    sample_project = Project(
        name="Sample SEO Project",
        description="A sample project for testing SEO Agent functionality",
        status=ProjectStatus.ACTIVE,
        owner_id=sample_user.id,
        target_domain="example.com",
        target_language="ja",
        target_audience="技術系のブログ読者",
        primary_keywords='["SEO", "コンテンツマーケティング", "AI"]',
        competitor_urls='["https://competitor1.com", "https://competitor2.com"]',
        tone_and_manner="専門的だが親しみやすい",
        brand_voice="革新的で信頼できる",
        content_guidelines="読者に価値を提供し、実用的な情報を含める",
    )
    db.add(sample_project)
    db.commit()
    
    print("✅ Database initialized with sample data")