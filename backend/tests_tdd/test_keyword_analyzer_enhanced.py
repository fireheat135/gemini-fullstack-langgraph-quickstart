"""
Enhanced Keyword Analyzer Tests
TDD implementation for Google Trends API and related keyword features
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import aiohttp

from src.seo.keyword_analyzer import KeywordAnalyzer


class TestKeywordAnalyzerEnhanced:
    """キーワード分析機能の拡張テスト"""
    
    @pytest.fixture
    def analyzer(self):
        return KeywordAnalyzer()
    
    @pytest.mark.asyncio
    async def test_get_related_keywords_from_suggestions(self, analyzer):
        """関連キーワード取得機能のテスト（サジェスト風）"""
        keyword = "3月 誕生花"
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.json = AsyncMock(return_value={
                "suggestions": [
                    "3月 誕生花 一覧",
                    "3月 誕生花 チューリップ",
                    "3月 誕生花 プレゼント",
                    "3月 誕生花 花言葉",
                    "3月 誕生花 ギフト"
                ]
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await analyzer.get_related_keywords_suggestions(keyword)
            
            assert "related_keywords" in result
            assert len(result["related_keywords"]) >= 5
            assert "3月 誕生花 一覧" in result["related_keywords"]
            assert "3月 誕生花 プレゼント" in result["related_keywords"]
    
    @pytest.mark.asyncio
    async def test_google_trends_integration(self, analyzer):
        """Google Trends API連携のテスト"""
        keyword = "誕生花"
        
        with patch('pytrends.request.TrendReq') as mock_trends:
            mock_trends_instance = Mock()
            mock_trends_instance.build_payload.return_value = None
            mock_trends_instance.interest_over_time.return_value = Mock(
                to_dict=Mock(return_value={
                    "誕生花": {
                        "2024-01-01": 100,
                        "2024-02-01": 85,
                        "2024-03-01": 120
                    }
                })
            )
            mock_trends_instance.related_queries.return_value = {
                "誕生花": {
                    "top": Mock(to_dict=Mock(return_value={
                        "query": ["誕生花 一覧", "誕生花 3月", "誕生花 花言葉"],
                        "value": [100, 85, 75]
                    }))
                }
            }
            mock_trends.return_value = mock_trends_instance
            
            result = await analyzer.get_google_trends_data(keyword)
            
            assert "interest_over_time" in result
            assert "related_queries" in result
            assert "peak_months" in result
            assert result["interest_over_time"]["誕生花"]["2024-03-01"] == 120
    
    @pytest.mark.asyncio
    async def test_keyword_difficulty_calculation_enhanced(self, analyzer):
        """強化されたキーワード難易度計算のテスト"""
        keyword = "3月 誕生花 プレゼント"
        
        with patch.multiple(
            analyzer,
            _get_search_volume=AsyncMock(return_value=2400),
            _get_competitor_count=AsyncMock(return_value=45000),
            _analyze_serp_competition=AsyncMock(return_value={
                "domain_authority_avg": 65,
                "content_quality_score": 78,
                "commercial_intent_ratio": 0.6
            })
        ):
            result = await analyzer.calculate_keyword_difficulty_enhanced(keyword)
            
            assert "difficulty_score" in result
            assert "search_volume" in result
            assert "competition_analysis" in result
            assert "recommendation" in result
            assert 0 <= result["difficulty_score"] <= 100
            assert result["search_volume"] == 2400
    
    @pytest.mark.asyncio
    async def test_semantic_keyword_analysis(self, analyzer):
        """セマンティック関連キーワード分析のテスト"""
        base_keyword = "誕生花"
        context = "プレゼント"
        
        # Mock word embeddings or semantic similarity
        with patch.object(analyzer, '_calculate_semantic_similarity') as mock_similarity:
            mock_similarity.side_effect = [0.85, 0.72, 0.91, 0.65, 0.88]
            
            candidate_keywords = [
                "花 ギフト",
                "花束 プレゼント", 
                "誕生日 花",
                "記念日 花",
                "季節の花"
            ]
            
            result = await analyzer.analyze_semantic_keywords(base_keyword, candidate_keywords, context)
            
            assert "semantic_matches" in result
            assert len(result["semantic_matches"]) > 0
            assert all(match["similarity_score"] >= 0.7 for match in result["semantic_matches"])
    
    @pytest.mark.asyncio
    async def test_competitor_keyword_analysis(self, analyzer):
        """競合キーワード分析のテスト"""
        competitor_urls = [
            "https://example-flower1.com",
            "https://example-flower2.com"
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.text = AsyncMock(return_value="""
            <html>
                <title>3月の誕生花 - チューリップの花言葉とプレゼント</title>
                <meta name="keywords" content="誕生花,3月,チューリップ,花言葉,プレゼント">
                <h1>3月の誕生花について</h1>
                <h2>チューリップの特徴</h2>
                <p>チューリップは3月の代表的な誕生花です。プレゼントとしても人気です。</p>
            </html>
            """)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await analyzer.analyze_competitor_keywords(competitor_urls)
            
            assert "extracted_keywords" in result
            assert "title_keywords" in result
            assert "meta_keywords" in result
            assert "heading_keywords" in result
            assert "keyword_frequency" in result
    
    @pytest.mark.asyncio
    async def test_seasonal_keyword_trends(self, analyzer):
        """季節性キーワードトレンド分析のテスト"""
        keyword = "誕生花"
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        with patch.object(analyzer, 'get_google_trends_data') as mock_trends:
            mock_trends.return_value = {
                "monthly_interest": {
                    1: 75, 2: 85, 3: 120, 4: 110, 5: 130,
                    6: 95, 7: 80, 8: 85, 9: 90, 10: 100, 11: 105, 12: 140
                }
            }
            
            result = await analyzer.analyze_seasonal_trends(keyword)
            
            assert "peak_months" in result
            assert "low_months" in result
            assert "seasonality_score" in result
            assert "monthly_distribution" in result
            assert 3 in result["peak_months"]  # March should be peak
            assert 12 in result["peak_months"]  # December should be peak
    
    @pytest.mark.asyncio
    async def test_long_tail_keyword_generation(self, analyzer):
        """ロングテールキーワード生成のテスト"""
        base_keyword = "誕生花"
        
        with patch.object(analyzer, '_get_search_suggestions') as mock_suggestions:
            mock_suggestions.return_value = [
                "誕生花 3月 プレゼント おすすめ",
                "誕生花 花言葉 意味 一覧",
                "誕生花 ギフト 通販 人気",
                "誕生花 アレンジメント 作り方"
            ]
            
            result = await analyzer.generate_long_tail_keywords(base_keyword)
            
            assert "long_tail_keywords" in result
            assert "difficulty_estimates" in result
            assert len(result["long_tail_keywords"]) >= 3
            assert all(len(kw.split()) >= 3 for kw in result["long_tail_keywords"])
    
    @pytest.mark.asyncio
    async def test_keyword_clustering(self, analyzer):
        """キーワードクラスタリングのテスト"""
        keywords = [
            "誕生花 3月",
            "3月 誕生花 チューリップ",
            "チューリップ 花言葉",
            "誕生花 プレゼント",
            "花 ギフト 3月",
            "春の花 プレゼント"
        ]
        
        result = await analyzer.cluster_keywords_by_intent(keywords)
        
        assert "clusters" in result
        assert "informational" in result["clusters"]
        assert "commercial" in result["clusters"]
        assert "navigational" in result["clusters"]
        assert len(result["clusters"]["informational"]) > 0
        assert len(result["clusters"]["commercial"]) > 0


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()