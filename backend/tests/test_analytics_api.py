"""Test cases for Analytics API."""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.models.base import Base
from src.models.user import User
from src.models.article import Article, ArticleStatus, ContentType
from src.api.deps import get_db


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_analytics.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(client):
    """Create test user for authentication."""
    db = TestingSessionLocal()
    user = User(
        email="analytics@example.com",
        username="analyticsuser",
        name="Analytics User",
        hashed_password="hashed_password",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers."""
    from src.api.deps import get_current_user
    
    def override_get_current_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    return {}


@pytest.fixture
def sample_articles(client, test_user):
    """Create sample articles for analytics testing."""
    db = TestingSessionLocal()
    
    articles = []
    
    # Create articles with different performance metrics
    article_data = [
        {
            "title": "高パフォーマンス記事: 誕生花の育て方",
            "content": "この記事は高いパフォーマンスを持つサンプル記事です。" * 50,
            "status": ArticleStatus.PUBLISHED,
            "page_views": 5000,
            "unique_visitors": 3000,
            "average_time_on_page": 240.5,
            "bounce_rate": 0.25,
            "conversion_rate": 0.05,
            "seo_score": 85.0,
            "readability_score": 80.0,
            "published_at": datetime.utcnow() - timedelta(days=7)
        },
        {
            "title": "中パフォーマンス記事: SEO最適化ガイド",
            "content": "この記事は中程度のパフォーマンスを持つサンプル記事です。" * 30,
            "status": ArticleStatus.PUBLISHED,
            "page_views": 2000,
            "unique_visitors": 1500,
            "average_time_on_page": 180.0,
            "bounce_rate": 0.45,
            "conversion_rate": 0.03,
            "seo_score": 70.0,
            "readability_score": 75.0,
            "published_at": datetime.utcnow() - timedelta(days=14)
        },
        {
            "title": "低パフォーマンス記事: テスト記事",
            "content": "この記事は低いパフォーマンスを持つサンプル記事です。" * 10,
            "status": ArticleStatus.PUBLISHED,
            "page_views": 500,
            "unique_visitors": 400,
            "average_time_on_page": 90.0,
            "bounce_rate": 0.70,
            "conversion_rate": 0.01,
            "seo_score": 45.0,
            "readability_score": 60.0,
            "published_at": datetime.utcnow() - timedelta(days=3)
        }
    ]
    
    for data in article_data:
        word_count = len(data["content"].split())
        article = Article(
            author_id=test_user.id,
            word_count=word_count,
            reading_time=max(1, round(word_count / 200)),
            **data
        )
        db.add(article)
        articles.append(article)
    
    db.commit()
    for article in articles:
        db.refresh(article)
    
    db.close()
    return articles


class TestAnalyticsAPI:
    """Analytics API test cases."""

    def test_get_analytics_summary(self, client, auth_headers, sample_articles):
        """Test getting analytics summary."""
        response = client.get("/api/v1/analytics/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_articles" in data
        assert "total_page_views" in data
        assert "total_unique_visitors" in data
        assert "average_seo_score" in data
        assert "average_bounce_rate" in data
        assert "top_performing_articles" in data
        
        # Verify calculated values
        assert data["total_articles"] == 3
        assert data["total_page_views"] == 7500  # 5000 + 2000 + 500
        assert data["total_unique_visitors"] == 4900  # 3000 + 1500 + 400

    def test_get_article_performance_comparison(self, client, auth_headers, sample_articles):
        """Test comparing article performance."""
        article_ids = [article.id for article in sample_articles[:2]]
        
        response = client.post(
            "/api/v1/analytics/compare",
            json={"article_ids": article_ids},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "comparison" in data
        assert len(data["comparison"]) == 2
        
        # Check comparison metrics
        for article_data in data["comparison"]:
            assert "id" in article_data
            assert "title" in article_data
            assert "performance_metrics" in article_data
            assert "page_views" in article_data["performance_metrics"]
            assert "seo_score" in article_data["performance_metrics"]

    def test_get_trend_analysis(self, client, auth_headers, sample_articles):
        """Test trend analysis over time."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        response = client.get(
            f"/api/v1/analytics/trends?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trends" in data
        assert "period" in data
        assert "metrics" in data["trends"]
        
        # Check trend metrics
        metrics = data["trends"]["metrics"]
        assert "page_views" in metrics
        assert "unique_visitors" in metrics
        assert "conversion_rate" in metrics

    def test_get_seo_performance_analysis(self, client, auth_headers, sample_articles):
        """Test SEO performance analysis."""
        response = client.get("/api/v1/analytics/seo-performance", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "seo_analysis" in data
        assert "average_seo_score" in data["seo_analysis"]
        assert "score_distribution" in data["seo_analysis"]
        assert "improvement_suggestions" in data["seo_analysis"]

    def test_get_content_performance_by_type(self, client, auth_headers, sample_articles):
        """Test content performance analysis by type."""
        response = client.get("/api/v1/analytics/content-performance", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content_performance" in data
        assert "by_content_type" in data["content_performance"]
        assert "by_word_count_range" in data["content_performance"]

    def test_get_user_engagement_metrics(self, client, auth_headers, sample_articles):
        """Test user engagement metrics."""
        response = client.get("/api/v1/analytics/engagement", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "engagement_metrics" in data
        assert "average_time_on_page" in data["engagement_metrics"]
        assert "bounce_rate" in data["engagement_metrics"]
        assert "page_depth" in data["engagement_metrics"]

    def test_get_conversion_analysis(self, client, auth_headers, sample_articles):
        """Test conversion analysis."""
        response = client.get("/api/v1/analytics/conversions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "conversion_analysis" in data
        assert "total_conversions" in data["conversion_analysis"]
        assert "conversion_rate" in data["conversion_analysis"]
        assert "top_converting_articles" in data["conversion_analysis"]

    def test_get_keyword_performance(self, client, auth_headers, sample_articles):
        """Test keyword performance analysis."""
        response = client.get("/api/v1/analytics/keywords", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "keyword_analysis" in data
        assert "top_keywords" in data["keyword_analysis"]
        assert "keyword_trends" in data["keyword_analysis"]

    def test_get_competitive_analysis(self, client, auth_headers, sample_articles):
        """Test competitive analysis."""
        response = client.get("/api/v1/analytics/competitive", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "competitive_analysis" in data
        assert "market_position" in data["competitive_analysis"]
        assert "opportunities" in data["competitive_analysis"]

    def test_analytics_date_filtering(self, client, auth_headers, sample_articles):
        """Test analytics with date filtering."""
        # Test last 7 days
        response = client.get("/api/v1/analytics/summary?days=7", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only include articles from last 7 days
        assert data["total_articles"] <= 3

    def test_export_analytics_report(self, client, auth_headers, sample_articles):
        """Test exporting analytics report."""
        response = client.get("/api/v1/analytics/export?format=json", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "report" in data
        assert "generated_at" in data
        assert "summary" in data["report"]
        assert "detailed_metrics" in data["report"]

    def test_analytics_unauthorized_access(self, client, sample_articles):
        """Test analytics API requires authentication."""
        app.dependency_overrides.clear()
        
        response = client.get("/api/v1/analytics/summary")
        assert response.status_code in [401, 403]

    def test_real_time_metrics(self, client, auth_headers, sample_articles):
        """Test real-time metrics endpoint."""
        response = client.get("/api/v1/analytics/real-time", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "real_time_metrics" in data
        assert "active_users" in data["real_time_metrics"]
        assert "current_page_views" in data["real_time_metrics"]
        assert "trending_articles" in data["real_time_metrics"]

    def test_custom_date_range_analytics(self, client, auth_headers, sample_articles):
        """Test analytics with custom date range."""
        start_date = (datetime.utcnow() - timedelta(days=20)).isoformat()
        end_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
        
        response = client.get(
            f"/api/v1/analytics/summary?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include articles within the specified range
        assert "total_articles" in data
        assert "date_range" in data