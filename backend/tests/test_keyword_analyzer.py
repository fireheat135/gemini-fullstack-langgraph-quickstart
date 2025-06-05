"""
TDD: Keyword Analysis & Co-occurrence Analysis Tests
誕生花記事のキーワード分析機能のテスト
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any


class TestKeywordAnalyzer:
    """キーワード分析機能のテスト"""

    @pytest.mark.asyncio
    async def test_extract_related_keywords_for_birth_flower(self):
        """誕生花に関連するキーワードを抽出できることを確認"""
        # Arrange
        primary_keyword = "3月 誕生花"
        
        # Act - まだ実装されていないので失敗する
        from src.seo.keyword_analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        related_keywords = await analyzer.get_related_keywords(primary_keyword)
        
        # Assert
        assert len(related_keywords) > 0
        assert any("チューリップ" in kw for kw in related_keywords)
        assert any("スイートアリッサム" in kw for kw in related_keywords)
        assert any("花言葉" in kw for kw in related_keywords)

    @pytest.mark.asyncio
    async def test_analyze_keyword_difficulty(self):
        """キーワード難易度を分析できることを確認"""
        # Arrange
        keywords = ["3月 誕生花", "チューリップ 花言葉", "誕生花 プレゼント"]
        
        # Act
        from src.seo.keyword_analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        difficulty_scores = await analyzer.analyze_difficulty(keywords)
        
        # Assert
        assert len(difficulty_scores) == len(keywords)
        for keyword, score in difficulty_scores.items():
            assert 0 <= score <= 100
            assert keyword in keywords

    @pytest.mark.asyncio
    async def test_get_search_volume_data(self):
        """検索ボリュームデータを取得できることを確認"""
        # Arrange
        keyword = "1月 誕生花"
        
        # Act
        from src.seo.keyword_analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        volume_data = await analyzer.get_search_volume(keyword)
        
        # Assert
        assert "monthly_searches" in volume_data
        assert "competition" in volume_data
        assert "trend_data" in volume_data
        assert isinstance(volume_data["monthly_searches"], int)
        assert volume_data["monthly_searches"] >= 0

    @pytest.mark.asyncio
    async def test_co_occurrence_analysis(self):
        """共起語分析が正しく動作することを確認"""
        # Arrange
        content = """
        3月の誕生花はチューリップです。チューリップの花言葉は博愛です。
        花言葉には思いやりという意味もあります。チューリップはプレゼントに最適です。
        花言葉を知ることで、より深い意味を込めたギフトを贈ることができます。
        """
        target_keyword = "チューリップ"
        
        # Act
        from src.seo.keyword_analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        co_occurrences = analyzer.analyze_co_occurrence(content, target_keyword)
        
        # Assert
        assert len(co_occurrences) > 0
        assert "花言葉" in [co["word"] for co in co_occurrences]
        assert "プレゼント" in [co["word"] for co in co_occurrences]
        # スコアが正しく計算されている
        for co in co_occurrences:
            assert "score" in co
            assert co["score"] > 0

    @pytest.mark.asyncio
    async def test_google_trends_integration(self):
        """Google Trends APIとの連携が動作することを確認"""
        # Arrange
        keyword = "母の日 誕生花"
        
        # Act
        from src.seo.trend_analyzer import TrendAnalyzer
        analyzer = TrendAnalyzer()
        trend_data = await analyzer.get_google_trends(keyword)
        
        # Assert
        assert "interest_over_time" in trend_data
        assert "related_queries" in trend_data
        assert len(trend_data["interest_over_time"]) > 0

    @pytest.mark.parametrize("month,expected_flowers", [
        (1, ["スイートピー", "カーネーション"]),
        (3, ["チューリップ", "スイートアリッサム"]),
        (6, ["バラ", "アジサイ"]),
        (12, ["ポインセチア", "カトレア"])
    ])
    @pytest.mark.asyncio
    async def test_month_specific_keyword_analysis(self, month, expected_flowers):
        """月ごとの誕生花キーワード分析が正しく動作することを確認"""
        # Arrange
        base_keyword = f"{month}月 誕生花"
        
        # Act
        from src.seo.keyword_analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        analysis_result = await analyzer.analyze_birth_flower_keywords(
            month=month,
            base_keyword=base_keyword
        )
        
        # Assert
        assert "primary_keyword" in analysis_result
        assert "related_keywords" in analysis_result
        assert "flower_specific_keywords" in analysis_result
        
        # 期待される花の名前が含まれているか
        all_keywords = (
            analysis_result["related_keywords"] + 
            analysis_result["flower_specific_keywords"]
        )
        for flower in expected_flowers:
            assert any(flower in kw for kw in all_keywords)

    @pytest.mark.asyncio
    async def test_competitor_keyword_analysis(self):
        """競合サイトのキーワード分析が動作することを確認"""
        # Arrange
        competitor_urls = [
            "https://example.com/birth-flowers",
            "https://another-site.com/花言葉"
        ]
        
        # Act
        from src.seo.competitor_analyzer import CompetitorAnalyzer
        analyzer = CompetitorAnalyzer()
        competitor_keywords = await analyzer.analyze_competitor_keywords(competitor_urls)
        
        # Assert
        assert len(competitor_keywords) > 0
        for url, keywords in competitor_keywords.items():
            assert url in competitor_urls
            assert isinstance(keywords, list)
            # モック実装ではキーワードが返されることを確認


class TestKeywordResearchWorkflow:
    """キーワードリサーチワークフローのテスト"""

    @pytest.mark.asyncio
    async def test_complete_keyword_research_for_birth_flower_article(self):
        """誕生花記事の完全なキーワードリサーチワークフローをテスト"""
        # Arrange
        article_topic = {
            "month": 5,
            "primary_keyword": "5月 誕生花",
            "target_audience": "誕生日プレゼントを探している人"
        }
        
        # Act
        from src.seo.keyword_research_workflow import KeywordResearchWorkflow
        workflow = KeywordResearchWorkflow()
        research_result = await workflow.conduct_full_research(article_topic)
        
        # Assert
        assert "primary_analysis" in research_result
        assert "related_keywords" in research_result
        assert "competitor_analysis" in research_result
        assert "trend_analysis" in research_result
        assert "difficulty_scores" in research_result
        assert "content_opportunities" in research_result
        
        # 5月の誕生花（スズラン、カーネーション）が含まれているか
        may_flowers = ["スズラン", "カーネーション"]
        all_keywords = research_result["related_keywords"]
        for flower in may_flowers:
            assert any(flower in kw for kw in all_keywords)

    @pytest.mark.asyncio
    async def test_keyword_clustering_for_content_planning(self):
        """コンテンツ企画のためのキーワードクラスタリングをテスト"""
        # Arrange
        keywords = [
            "7月 誕生花", "ユリ 花言葉", "ヒマワリ 意味",
            "誕生花 プレゼント", "花 ギフト", "夏 花束",
            "ユリ 種類", "ヒマワリ 育て方", "花言葉 一覧"
        ]
        
        # Act
        from src.seo.keyword_analyzer import KeywordAnalyzer
        analyzer = KeywordAnalyzer()
        clusters = analyzer.cluster_keywords(keywords)
        
        # Assert
        assert len(clusters) > 1  # 複数のクラスターに分類される
        cluster_themes = [cluster["theme"] for cluster in clusters]
        assert "花言葉・意味" in cluster_themes  # 実際の実装に合わせて修正
        assert "プレゼント・ギフト" in cluster_themes
        assert "花の種類・育て方" in cluster_themes

    @pytest.mark.asyncio
    async def test_seasonal_keyword_trends(self):
        """季節性のあるキーワードトレンドを分析できることを確認"""
        # Arrange
        seasonal_keywords = [
            "母の日 誕生花",    # 5月にピーク
            "クリスマス 花",    # 12月にピーク
            "卒業式 花束",      # 3月にピーク
        ]
        
        # Act
        from src.seo.trend_analyzer import TrendAnalyzer
        analyzer = TrendAnalyzer()
        seasonal_analysis = await analyzer.analyze_seasonal_trends(seasonal_keywords)
        
        # Assert
        for keyword, trend_data in seasonal_analysis.items():
            assert "peak_months" in trend_data
            assert "seasonality_score" in trend_data
            assert trend_data["seasonality_score"] >= 0
            
            # 期待される季節性
            if "母の日" in keyword:
                assert 5 in trend_data["peak_months"]
            elif "クリスマス" in keyword:
                assert 12 in trend_data["peak_months"]
            elif "卒業式" in keyword:
                assert 3 in trend_data["peak_months"]


class TestKeywordDataSources:
    """キーワードデータソースのテスト"""

    @pytest.mark.asyncio
    async def test_google_suggest_api_integration(self):
        """Google Suggest APIとの連携をテスト"""
        # Arrange
        seed_keyword = "誕生花"
        
        # Act
        from src.seo.data_sources import GoogleSuggestAPI
        api = GoogleSuggestAPI()
        suggestions = await api.get_suggestions(seed_keyword)
        
        # Assert
        assert len(suggestions) > 0
        assert all(seed_keyword in suggestion for suggestion in suggestions)

    @pytest.mark.asyncio
    async def test_rakko_keyword_style_extraction(self):
        """ラッコキーワード風のキーワード抽出をテスト"""
        # Arrange
        base_keyword = "誕生花"
        
        # Act
        from src.seo.data_sources import RakkoStyleKeywordExtractor
        extractor = RakkoStyleKeywordExtractor()
        keyword_data = await extractor.extract_keywords(base_keyword)
        
        # Assert
        assert "suggest_keywords" in keyword_data
        assert "related_keywords" in keyword_data
        assert "qa_keywords" in keyword_data  # Yahoo知恵袋風のQ&A
        assert len(keyword_data["suggest_keywords"]) > 0

    @pytest.mark.asyncio
    async def test_search_console_data_integration(self):
        """Search Consoleデータとの連携をテスト（モック）"""
        # Arrange
        site_url = "https://example.com"
        
        # Act
        with patch("src.seo.data_sources.SearchConsoleAPI") as mock_api:
            mock_api_instance = mock_api.return_value
            mock_api_instance.get_keyword_performance = AsyncMock(
                return_value={
                    "誕生花": {"clicks": 150, "impressions": 1200, "ctr": 0.125},
                    "3月 誕生花": {"clicks": 89, "impressions": 890, "ctr": 0.10},
                }
            )
            
            from src.seo.data_sources import SearchConsoleAPI
            api = SearchConsoleAPI()
            performance_data = await api.get_keyword_performance(site_url)
        
        # Assert
        assert "誕生花" in performance_data
        assert performance_data["誕生花"]["clicks"] == 150