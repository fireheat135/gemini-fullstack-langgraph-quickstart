"""
Test suite for Keyword Research API endpoints
Following TDD approach - tests written before implementation
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.user import User
from src.models.api_key import APIKey, APIProvider


class TestKeywordResearchAPI:
    """Test keyword research functionality through API endpoints"""
    
    @pytest.fixture
    def auth_headers(self, client: TestClient, db: Session) -> dict:
        """Create authenticated user and return auth headers"""
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Create API key for user
        api_key = APIKey(
            user_id=user.id,
            provider=APIProvider.GOOGLE_GEMINI,
            encrypted_key="encrypted_test_key",
            is_active=True
        )
        db.add(api_key)
        db.commit()
        
        # Login and get token
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test@example.com", "password": "password"}
        )
        token = response.json()["access_token"]
        
        return {"Authorization": f"Bearer {token}"}
    
    def test_analyze_keyword_basic(self, client: TestClient, auth_headers: dict):
        """Test basic keyword analysis functionality"""
        # Arrange
        keyword_data = {
            "keyword": "SEO最適化コンテンツ",
            "include_trends": True,
            "include_related": True,
            "include_competitors": False
        }
        
        # Act
        response = client.post(
            "/api/v1/keywords/analyze",
            json=keyword_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "keyword" in data
        assert data["keyword"] == "SEO最適化コンテンツ"
        assert "search_volume" in data
        assert "difficulty" in data
        assert "trend" in data
        assert "related_keywords" in data
        assert isinstance(data["related_keywords"], list)
        
    def test_bulk_keyword_analysis(self, client: TestClient, auth_headers: dict):
        """Test bulk keyword analysis from CSV"""
        # Arrange
        keywords = [
            "SEO最適化",
            "コンテンツマーケティング",
            "キーワードリサーチ"
        ]
        
        # Act
        response = client.post(
            "/api/v1/keywords/analyze/bulk",
            json={"keywords": keywords},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert len(data["results"]) == 3
        
        for result in data["results"]:
            assert "keyword" in result
            assert "search_volume" in result
            assert "difficulty" in result
            assert result["keyword"] in keywords
    
    def test_competitor_analysis(self, client: TestClient, auth_headers: dict):
        """Test competitor analysis for a keyword"""
        # Arrange
        request_data = {
            "keyword": "SEO最適化コンテンツ",
            "top_n": 10
        }
        
        # Act
        response = client.post(
            "/api/v1/keywords/competitors",
            json=request_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "keyword" in data
        assert "competitors" in data
        assert isinstance(data["competitors"], list)
        assert len(data["competitors"]) <= 10
        
        if data["competitors"]:
            competitor = data["competitors"][0]
            assert "url" in competitor
            assert "title" in competitor
            assert "meta_description" in competitor
            assert "word_count" in competitor
            assert "headings" in competitor
            assert "ranking_position" in competitor
    
    def test_keyword_clustering(self, client: TestClient, auth_headers: dict):
        """Test keyword clustering functionality"""
        # Arrange
        keywords = [
            "SEO最適化",
            "SEO対策",
            "検索エンジン最適化",
            "コンテンツSEO",
            "キーワードリサーチ",
            "キーワード選定"
        ]
        
        # Act
        response = client.post(
            "/api/v1/keywords/cluster",
            json={"keywords": keywords},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "clusters" in data
        assert isinstance(data["clusters"], list)
        
        for cluster in data["clusters"]:
            assert "name" in cluster
            assert "keywords" in cluster
            assert isinstance(cluster["keywords"], list)
            assert all(kw in keywords for kw in cluster["keywords"])
    
    def test_trend_analysis(self, client: TestClient, auth_headers: dict):
        """Test trend analysis over time"""
        # Arrange
        request_data = {
            "keyword": "SEO最適化",
            "timeframe": "12_months"
        }
        
        # Act
        response = client.post(
            "/api/v1/keywords/trends",
            json=request_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "keyword" in data
        assert "trend_data" in data
        assert isinstance(data["trend_data"], list)
        
        if data["trend_data"]:
            trend_point = data["trend_data"][0]
            assert "date" in trend_point
            assert "value" in trend_point
            assert "normalized_value" in trend_point
    
    def test_csv_import(self, client: TestClient, auth_headers: dict):
        """Test importing keywords from CSV file"""
        # Arrange
        csv_content = """keyword,search_volume,cpc
SEO最適化,5400,150
コンテンツマーケティング,3200,200
キーワードリサーチ,1800,100"""
        
        files = {
            "file": ("keywords.csv", csv_content, "text/csv")
        }
        
        # Act
        response = client.post(
            "/api/v1/keywords/import/csv",
            files=files,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "imported_count" in data
        assert data["imported_count"] == 3
        assert "keywords" in data
        assert len(data["keywords"]) == 3
    
    def test_keyword_suggestions(self, client: TestClient, auth_headers: dict):
        """Test AI-powered keyword suggestions"""
        # Arrange
        request_data = {
            "seed_keyword": "SEO最適化",
            "target_audience": "マーケティング担当者",
            "content_type": "ブログ記事",
            "suggestion_count": 10
        }
        
        # Act
        response = client.post(
            "/api/v1/keywords/suggest",
            json=request_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) <= 10
        
        for suggestion in data["suggestions"]:
            assert "keyword" in suggestion
            assert "relevance_score" in suggestion
            assert "reasoning" in suggestion
    
    def test_search_volume_history(self, client: TestClient, auth_headers: dict):
        """Test retrieving historical search volume data"""
        # Arrange
        keyword = "SEO最適化"
        
        # Act
        response = client.get(
            f"/api/v1/keywords/{keyword}/history",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "keyword" in data
        assert "history" in data
        assert isinstance(data["history"], list)
        
        if data["history"]:
            history_point = data["history"][0]
            assert "month" in history_point
            assert "search_volume" in history_point
            assert "year_over_year_change" in history_point
    
    def test_keyword_difficulty_calculation(self, client: TestClient, auth_headers: dict):
        """Test keyword difficulty score calculation"""
        # Arrange
        request_data = {
            "keyword": "SEO最適化コンテンツ",
            "include_breakdown": True
        }
        
        # Act
        response = client.post(
            "/api/v1/keywords/difficulty",
            json=request_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "keyword" in data
        assert "difficulty_score" in data
        assert 0 <= data["difficulty_score"] <= 100
        
        assert "breakdown" in data
        breakdown = data["breakdown"]
        assert "domain_authority_avg" in breakdown
        assert "backlinks_avg" in breakdown
        assert "content_quality_avg" in breakdown
        assert "serp_features" in breakdown
    
    def test_missing_api_key(self, client: TestClient, db: Session):
        """Test handling of missing API key"""
        # Create user without API key
        user = User(
            email="noapi@example.com",
            username="noapiuser",
            hashed_password="hashed_password",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "noapi@example.com", "password": "password"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to analyze keyword
        response = client.post(
            "/api/v1/keywords/analyze",
            json={"keyword": "test"},
            headers=headers
        )
        
        assert response.status_code == 400
        assert "API key not configured" in response.json()["detail"]
    
    def test_rate_limiting(self, client: TestClient, auth_headers: dict):
        """Test API rate limiting"""
        # Make multiple rapid requests
        responses = []
        for i in range(15):  # Assuming rate limit is 10 per minute
            response = client.post(
                "/api/v1/keywords/analyze",
                json={"keyword": f"test{i}"},
                headers=auth_headers
            )
            responses.append(response)
        
        # Check that some requests were rate limited
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0
        
        # Check rate limit headers
        limited_response = rate_limited[0]
        assert "X-RateLimit-Limit" in limited_response.headers
        assert "X-RateLimit-Remaining" in limited_response.headers
        assert "X-RateLimit-Reset" in limited_response.headers