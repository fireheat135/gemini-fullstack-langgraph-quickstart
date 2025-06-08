"""
Test Suite for Content Management System
過去記事管理・重複検出システムのテスト

Test Coverage:
1. 過去記事のコンテンツ・トンマナ保存機能
2. 記事間重複コンテンツ検出
3. 類似度判定アルゴリズム
4. 重複アラート機能
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio

from src.content.content_management_system import (
    ContentManagementSystem,
    ArticleContent,
    DuplicateDetectionResult,
    SimilarityAnalysis,
    ContentAlert,
    ToneManner,
    AlertType,
    SimilarityThreshold
)


class TestContentManagementSystem:
    
    @pytest.fixture
    def cms(self):
        """Content Management System instance for testing"""
        return ContentManagementSystem()
    
    @pytest.fixture
    def sample_articles(self) -> List[ArticleContent]:
        """テスト用の記事データ"""
        return [
            ArticleContent(
                id="article_1",
                title="1月の誕生花「カーネーション」の花言葉と育て方",
                content="カーネーションは1月を代表する美しい花です。花言葉は「母への愛」「感謝」を表しています。",
                keyword="1月 誕生花 カーネーション",
                tone_manner=ToneManner(
                    tone="親しみやすい",
                    formality="カジュアル",
                    target_audience="花好きの女性",
                    writing_style="情報提供型"
                ),
                created_at=datetime.now() - timedelta(days=30),
                meta_description="1月の誕生花カーネーションの花言葉と育て方を詳しく解説",
                tags=["誕生花", "1月", "カーネーション", "花言葉"]
            ),
            ArticleContent(
                id="article_2", 
                title="2月の誕生花「プリムラ」の特徴と花言葉",
                content="プリムラは2月の代表的な誕生花として親しまれています。可憐な花びらと豊富な色彩が魅力的です。",
                keyword="2月 誕生花 プリムラ",
                tone_manner=ToneManner(
                    tone="親しみやすい",
                    formality="カジュアル", 
                    target_audience="花好きの女性",
                    writing_style="情報提供型"
                ),
                created_at=datetime.now() - timedelta(days=20),
                meta_description="2月の誕生花プリムラの特徴と美しい花言葉について",
                tags=["誕生花", "2月", "プリムラ", "花言葉"]
            ),
            ArticleContent(
                id="article_3",
                title="カーネーションの育て方完全ガイド",
                content="カーネーションは比較的育てやすい花として知られています。適切な水やりと日光管理が重要なポイントです。",
                keyword="カーネーション 育て方",
                tone_manner=ToneManner(
                    tone="親しみやすい",
                    formality="カジュアル",
                    target_audience="ガーデニング初心者", 
                    writing_style="問題解決型"
                ),
                created_at=datetime.now() - timedelta(days=10),
                meta_description="カーネーションの育て方を初心者向けに詳しく解説",
                tags=["カーネーション", "育て方", "ガーデニング"]
            )
        ]

    # ===== 記事保存・管理機能のテスト =====
    
    def test_store_article_content(self, cms, sample_articles):
        """記事コンテンツの保存テスト"""
        article = sample_articles[0]
        
        result = cms.store_article(article)
        
        assert result.success == True
        assert result.article_id == "article_1"
        assert "記事が正常に保存されました" in result.message
    
    def test_retrieve_article_by_id(self, cms, sample_articles):
        """記事IDによる取得テスト"""
        article = sample_articles[0]
        cms.store_article(article)
        
        retrieved = cms.get_article_by_id("article_1")
        
        assert retrieved is not None
        assert retrieved.id == "article_1"
        assert retrieved.title == article.title
        assert retrieved.content == article.content
    
    def test_retrieve_articles_by_keyword(self, cms, sample_articles):
        """キーワードによる記事検索テスト"""
        for article in sample_articles:
            cms.store_article(article)
        
        results = cms.get_articles_by_keyword("カーネーション")
        
        assert len(results) == 2  # article_1 and article_3
        assert all("カーネーション" in article.keyword for article in results)
    
    def test_retrieve_articles_by_date_range(self, cms, sample_articles):
        """日付範囲による記事検索テスト"""
        for article in sample_articles:
            cms.store_article(article)
        
        start_date = datetime.now() - timedelta(days=25)
        end_date = datetime.now() - timedelta(days=5)
        
        results = cms.get_articles_by_date_range(start_date, end_date)
        
        assert len(results) >= 1
        assert all(start_date <= article.created_at <= end_date for article in results)

    # ===== 重複検出機能のテスト =====
    
    def test_detect_exact_duplicate_content(self, cms, sample_articles):
        """完全重複コンテンツの検出テスト"""
        article1 = sample_articles[0]
        article2 = ArticleContent(
            id="duplicate_article",
            title="違うタイトル",
            content=article1.content,  # 同じコンテンツ
            keyword="別のキーワード",
            tone_manner=article1.tone_manner,
            created_at=datetime.now()
        )
        
        cms.store_article(article1)
        
        result = cms.detect_duplicates(article2)
        
        assert result.has_duplicates == True
        assert len(result.exact_matches) == 1
        assert result.exact_matches[0].article_id == "article_1"
        assert result.exact_matches[0].similarity_score == 1.0
    
    def test_detect_partial_duplicate_content(self, cms, sample_articles):
        """部分重複コンテンツの検出テスト"""
        article1 = sample_articles[0]
        article2 = ArticleContent(
            id="partial_duplicate",
            title="部分的に似た記事",
            content="カーネーションは1月を代表する花です。美しい花言葉を持っています。",  # 部分的に類似
            keyword="カーネーション 花言葉",
            tone_manner=article1.tone_manner,
            created_at=datetime.now()
        )
        
        cms.store_article(article1)
        
        result = cms.detect_duplicates(article2)
        
        assert result.has_duplicates == True
        assert len(result.partial_matches) >= 1
        similarity_score = result.partial_matches[0].similarity_score
        assert 0.3 <= similarity_score < 1.0  # 部分的類似のスコア範囲

    def test_detect_similar_tone_manner(self, cms, sample_articles):
        """トンマナ類似性の検出テスト"""
        for article in sample_articles[:2]:  # 同じトンマナの記事を保存
            cms.store_article(article)
        
        new_article = ArticleContent(
            id="similar_tone",
            title="新しい記事",
            content="全く違うコンテンツですが、同じトンマナです。",
            keyword="新しいキーワード",
            tone_manner=sample_articles[0].tone_manner,  # 同じトンマナ
            created_at=datetime.now()
        )
        
        result = cms.detect_duplicates(new_article)
        
        assert len(result.tone_manner_matches) >= 2

    # ===== 類似度判定アルゴリズムのテスト =====
    
    def test_cosine_similarity_calculation(self, cms):
        """コサイン類似度計算のテスト"""
        text1 = "カーネーションは美しい花です"
        text2 = "カーネーションは美しい花として知られています"
        text3 = "プリムラは可憐な花です"
        
        similarity_12 = cms.calculate_cosine_similarity(text1, text2)
        similarity_13 = cms.calculate_cosine_similarity(text1, text3)
        
        assert similarity_12 > similarity_13  # より類似したテキストの方が高いスコア
        assert 0 <= similarity_12 <= 1
        assert 0 <= similarity_13 <= 1
    
    def test_jaccard_similarity_calculation(self, cms):
        """Jaccard類似度計算のテスト"""
        text1 = "カーネーション 花言葉 美しい"
        text2 = "カーネーション 花言葉 育て方"
        text3 = "プリムラ 特徴 色彩"
        
        similarity_12 = cms.calculate_jaccard_similarity(text1, text2)
        similarity_13 = cms.calculate_jaccard_similarity(text1, text3)
        
        assert similarity_12 > similarity_13
        assert 0 <= similarity_12 <= 1
        assert 0 <= similarity_13 <= 1
    
    def test_semantic_similarity_analysis(self, cms):
        """意味的類似度分析のテスト"""
        analysis = cms.analyze_semantic_similarity(
            "1月の誕生花はカーネーションです",
            "カーネーションは1月を代表する花です"
        )
        
        assert isinstance(analysis, SimilarityAnalysis)
        assert 0 <= analysis.cosine_score <= 1
        assert 0 <= analysis.jaccard_score <= 1
        assert 0 <= analysis.semantic_score <= 1
        assert analysis.overall_score > 0.5  # 意味的に類似
    
    def test_tone_manner_similarity(self, cms, sample_articles):
        """トンマナ類似度計算のテスト"""
        tone1 = sample_articles[0].tone_manner
        tone2 = sample_articles[1].tone_manner  # 同じトンマナ
        tone3 = ToneManner(
            tone="フォーマル",
            formality="丁寧",
            target_audience="ビジネスマン",
            writing_style="比較検討型"
        )
        
        similarity_12 = cms.calculate_tone_manner_similarity(tone1, tone2)
        similarity_13 = cms.calculate_tone_manner_similarity(tone1, tone3)
        
        assert similarity_12 > similarity_13
        assert similarity_12 == 1.0  # 完全に同じトンマナ

    # ===== アラート機能のテスト =====
    
    def test_generate_duplicate_alert(self, cms, sample_articles):
        """重複アラート生成のテスト"""
        article1 = sample_articles[0]
        cms.store_article(article1)
        
        duplicate_article = ArticleContent(
            id="duplicate_test",
            title="重複テスト記事",
            content=article1.content,  # 同じコンテンツ
            keyword="重複テストキーワード",
            tone_manner=article1.tone_manner,
            created_at=datetime.now()
        )
        
        alerts = cms.generate_content_alerts(duplicate_article)
        
        assert len(alerts) >= 1
        duplicate_alert = next((a for a in alerts if a.alert_type == AlertType.EXACT_DUPLICATE), None)
        assert duplicate_alert is not None
        assert duplicate_alert.severity == "HIGH"
        assert "完全重複" in duplicate_alert.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF < /dev/null