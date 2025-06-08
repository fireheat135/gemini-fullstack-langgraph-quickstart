"""Test cases for Content Management API."""

import pytest
from datetime import datetime
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
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_content.db"

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
        email="test@example.com",
        username="testuser",
        name="Test User",
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
    # For testing, we'll mock the authentication
    # by directly overriding the get_current_user dependency
    from src.api.deps import get_current_user
    
    def override_get_current_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    return {}  # No headers needed since we override the dependency


@pytest.fixture
def sample_article_data():
    """Sample article data for testing."""
    return {
        "title": "Test Article: 誕生花で学ぶSEO最適化",
        "content": "これは誕生花についてのテスト記事です。" * 50,  # 長いコンテンツ
        "meta_title": "誕生花SEO最適化ガイド",
        "meta_description": "誕生花をテーマにしたSEO最適化の完全ガイド。検索エンジンで上位表示を狙います。",
        "content_type": "blog_post",
        "status": "draft",
        "target_keywords": "誕生花,SEO,最適化,ガーデニング",
        "ai_generated": True,
        "ai_model_used": "gemini-pro"
    }


class TestContentAPI:
    """Content Management API test cases."""

    def test_create_article_success(self, client, auth_headers, sample_article_data):
        """Test successful article creation."""
        response = client.post(
            "/api/v1/content/articles/",
            json=sample_article_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["title"] == sample_article_data["title"]
        assert data["status"] == "draft"
        assert data["ai_generated"] is True
        assert data["word_count"] > 0  # Should be calculated
        assert data["created_at"] is not None

    def test_create_article_missing_title(self, client, auth_headers):
        """Test article creation fails without title."""
        invalid_data = {
            "content": "Content without title",
            "status": "draft"
        }
        
        response = client.post(
            "/api/v1/content/articles/",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error

    def test_get_articles_list(self, client, auth_headers, sample_article_data):
        """Test retrieving articles list."""
        # Create some test articles
        for i in range(3):
            article_data = sample_article_data.copy()
            article_data["title"] = f"Test Article {i+1}"
            client.post("/api/v1/content/articles/", json=article_data, headers=auth_headers)
        
        # Get articles list
        response = client.get("/api/v1/content/articles/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 3
        assert data["total"] >= 3

    def test_get_articles_with_pagination(self, client, auth_headers, sample_article_data):
        """Test articles list with pagination."""
        # Create test articles
        for i in range(5):
            article_data = sample_article_data.copy()
            article_data["title"] = f"Article {i+1}"
            client.post("/api/v1/content/articles/", json=article_data, headers=auth_headers)
        
        # Test pagination
        response = client.get("/api/v1/content/articles/?skip=2&limit=2", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_get_article_by_id(self, client, auth_headers, sample_article_data):
        """Test retrieving specific article by ID."""
        # Create article
        create_response = client.post(
            "/api/v1/content/articles/",
            json=sample_article_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        article_id = create_response.json()["id"]
        
        # Get article by ID
        response = client.get(f"/api/v1/content/articles/{article_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id
        assert data["title"] == sample_article_data["title"]

    def test_get_nonexistent_article(self, client, auth_headers):
        """Test retrieving non-existent article returns 404."""
        response = client.get("/api/v1/content/articles/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_update_article(self, client, auth_headers, sample_article_data):
        """Test updating existing article."""
        # Create article
        create_response = client.post(
            "/api/v1/content/articles/",
            json=sample_article_data,
            headers=auth_headers
        )
        article_id = create_response.json()["id"]
        
        # Update article
        update_data = {
            "title": "Updated Title: 誕生花SEO完全ガイド",
            "status": "review",
            "content": "Updated content with more SEO information."
        }
        
        response = client.put(
            f"/api/v1/content/articles/{article_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["status"] == "review"
        assert data["updated_at"] is not None

    def test_delete_article(self, client, auth_headers, sample_article_data):
        """Test deleting article."""
        # Create article
        create_response = client.post(
            "/api/v1/content/articles/",
            json=sample_article_data,
            headers=auth_headers
        )
        article_id = create_response.json()["id"]
        
        # Delete article
        response = client.delete(f"/api/v1/content/articles/{article_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/v1/content/articles/{article_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_publish_article(self, client, auth_headers, sample_article_data):
        """Test publishing article."""
        # Create draft article
        create_response = client.post(
            "/api/v1/content/articles/",
            json=sample_article_data,
            headers=auth_headers
        )
        article_id = create_response.json()["id"]
        
        # Publish article
        response = client.post(
            f"/api/v1/content/articles/{article_id}/publish",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert data["published_at"] is not None

    def test_search_articles(self, client, auth_headers, sample_article_data):
        """Test searching articles by title/content."""
        # Create articles with different content
        articles_data = [
            {**sample_article_data, "title": "誕生花の育て方", "content": "誕生花を育てる方法について"},
            {**sample_article_data, "title": "SEO最適化ガイド", "content": "検索エンジン最適化のベストプラクティス"},
            {**sample_article_data, "title": "ガーデニング入門", "content": "初心者向けガーデニングガイド"}
        ]
        
        for article_data in articles_data:
            client.post("/api/v1/content/articles/", json=article_data, headers=auth_headers)
        
        # Search for articles
        response = client.get("/api/v1/content/articles/?search=誕生花", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert any("誕生花" in item["title"] for item in data["items"])

    def test_filter_articles_by_status(self, client, auth_headers, sample_article_data):
        """Test filtering articles by status."""
        # Create articles with different statuses
        statuses = ["draft", "review", "published"]
        for status in statuses:
            article_data = sample_article_data.copy()
            article_data["status"] = status
            article_data["title"] = f"Article with {status} status"
            client.post("/api/v1/content/articles/", json=article_data, headers=auth_headers)
        
        # Filter by status
        response = client.get("/api/v1/content/articles/?status=draft", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["status"] == "draft" for item in data["items"])

    def test_get_article_analytics(self, client, auth_headers, sample_article_data):
        """Test retrieving article analytics."""
        # Create and publish article
        create_response = client.post(
            "/api/v1/content/articles/",
            json=sample_article_data,
            headers=auth_headers
        )
        article_id = create_response.json()["id"]
        
        # Publish article first
        client.post(f"/api/v1/content/articles/{article_id}/publish", headers=auth_headers)
        
        # Get analytics
        response = client.get(f"/api/v1/content/articles/{article_id}/analytics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "page_views" in data
        assert "seo_score" in data
        assert "word_count" in data

    def test_unauthorized_access(self, client, sample_article_data):
        """Test API requires authentication."""
        # Clear dependency overrides to test actual authentication
        app.dependency_overrides.clear()
        
        response = client.post("/api/v1/content/articles/", json=sample_article_data)
        assert response.status_code in [401, 403]  # Unauthorized or Forbidden

    def test_calculate_word_count(self, client, auth_headers):
        """Test automatic word count calculation."""
        article_data = {
            "title": "Word Count Test",
            "content": "This is a test content with exactly ten words.",
            "status": "draft"
        }
        
        response = client.post(
            "/api/v1/content/articles/",
            json=article_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["word_count"] == 10

    def test_calculate_reading_time(self, client, auth_headers):
        """Test automatic reading time calculation."""
        # Average reading speed: ~200 words per minute
        long_content = " ".join(["word"] * 400)  # 400 words
        
        article_data = {
            "title": "Reading Time Test",
            "content": long_content,
            "status": "draft"
        }
        
        response = client.post(
            "/api/v1/content/articles/",
            json=article_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["reading_time"] == 2  # 400 words / 200 wpm = 2 minutes