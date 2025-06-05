"""
Test for Tone & Manner Engine
トーン&マナーエンジンのテスト
TDD Red Phase: 一貫性チェック機能のテスト作成
"""
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from datetime import datetime


@pytest.fixture
def sample_article_with_tone():
    """トーンプロファイル付きのサンプル記事"""
    return {
        "id": "article_001",
        "title": "3月の誕生花チューリップの花言葉と魅力",
        "content": """
        3月の誕生花であるチューリップは、春の訪れを告げる美しい花として親しまれています。
        その鮮やかな色彩と優雅な形状で、多くの人々に愛され続けています。
        チューリップの花言葉は「思いやり」「美しい眼差し」「正直」などがあります。
        実際に選ぶ際のポイントとしては、色合いや品種の特徴を理解することが大切です。
        """,
        "tone_profile": {
            "writing_style": "friendly_casual",
            "target_audience": "30代女性プレゼント購入検討者",
            "brand_voice": "親しみやすく専門的",
            "formality_level": "やや丁寧",
            "emotional_tone": "warm_helpful",
            "sample_phrases": ["実際に", "〜ですよね", "大切です", "おすすめ"],
            "prohibited_expressions": ["絶対に", "必ず", "100%"]
        }
    }


@pytest.fixture
def inconsistent_article():
    """一貫性のない記事サンプル"""
    return {
        "id": "article_002", 
        "title": "4月の誕生花について専門的に解説します",
        "content": """
        4月の誕生花に関して、専門的見地から詳細にご説明申し上げます。
        本花卉につきましては、学術的分類において重要な位置を占めております。
        絶対に覚えておくべきポイントは、必ず品種の特性を100%理解することです。
        ちょっと気になるのが、みんな知らない秘密の情報なんですよね。
        """,
        "tone_profile": {
            "writing_style": "friendly_casual",
            "target_audience": "30代女性プレゼント購入検討者", 
            "brand_voice": "親しみやすく専門的",
            "formality_level": "やや丁寧",
            "emotional_tone": "warm_helpful"
        }
    }


@pytest.fixture
def brand_guidelines():
    """ブランドガイドライン"""
    return {
        "brand_personality": "温かく信頼できる専門的",
        "target_relationship": "友人のようなアドバイザー",
        "expertise_level": "中級者向け",
        "voice_attributes": ["親しみやすい", "知識豊富", "共感的"],
        "do_phrases": [
            "一緒に考えてみましょう",
            "お手伝いさせていただきます",
            "実際に選ぶ際は"
        ],
        "dont_phrases": [
            "絶対に", "必ず", "100%", "買わないと損",
            "申し上げます", "ご説明申し上げます"
        ],
        "consistency_rules": [
            "同じトーンを記事全体で維持する",
            "読者との距離感を一定に保つ",
            "専門用語の使用レベルを統一する"
        ]
    }


class TestToneMannerEngine:
    """トーン&マナーエンジンのテストクラス"""

    def test_compare_tone_with_past_articles_過去記事とのトンマナ比較(self, sample_article_with_tone):
        """過去記事とのトーン&マナー比較機能をテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        # 過去記事のデータベース（mock）
        past_articles = [
            {
                "id": "past_001",
                "tone_profile": {
                    "writing_style": "friendly_casual",
                    "formality_level": "やや丁寧",
                    "emotional_tone": "warm_helpful"
                }
            }
        ]
        
        # 比較結果を取得
        comparison_result = engine.compare_with_past_articles(
            sample_article_with_tone,
            past_articles
        )
        
        assert comparison_result is not None
        assert "consistency_score" in comparison_result
        assert "matching_articles" in comparison_result
        assert "tone_variations" in comparison_result
        assert 0.0 <= comparison_result["consistency_score"] <= 1.0

    def test_writing_style_consistency_check_文体一貫性チェック(self, sample_article_with_tone, inconsistent_article):
        """文体・表現一貫性チェック機能をテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        # 一貫性のある記事のチェック
        consistent_result = engine.check_writing_consistency(sample_article_with_tone)
        
        assert consistent_result is not None
        assert "is_consistent" in consistent_result
        assert "consistency_issues" in consistent_result
        assert "consistency_score" in consistent_result
        assert consistent_result["is_consistent"] is True
        
        # 一貫性のない記事のチェック
        inconsistent_result = engine.check_writing_consistency(inconsistent_article)
        
        assert inconsistent_result["is_consistent"] is False
        assert len(inconsistent_result["consistency_issues"]) > 0
        assert inconsistent_result["consistency_score"] < 0.8

    def test_brand_voice_compatibility_evaluation_ブランドボイス適合性評価(self, sample_article_with_tone, brand_guidelines):
        """ブランドボイス適合性評価システムをテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        compatibility_result = engine.evaluate_brand_voice_compatibility(
            sample_article_with_tone,
            brand_guidelines
        )
        
        assert compatibility_result is not None
        assert "compatibility_score" in compatibility_result
        assert "compliance_issues" in compatibility_result
        assert "brand_alignment" in compatibility_result
        assert 0.0 <= compatibility_result["compatibility_score"] <= 1.0

    def test_detect_prohibited_expressions_禁止表現検出(self, inconsistent_article, brand_guidelines):
        """禁止表現の検出をテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        prohibited_result = engine.detect_prohibited_expressions(
            inconsistent_article["content"],
            brand_guidelines["dont_phrases"]
        )
        
        assert prohibited_result is not None
        assert "violations_found" in prohibited_result
        assert "violation_details" in prohibited_result
        assert prohibited_result["violations_found"] is True
        assert len(prohibited_result["violation_details"]) > 0

    def test_tone_drift_detection_トーンドリフト検出(self, sample_article_with_tone):
        """記事内でのトーンの変化（ドリフト）検出をテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        # 記事を段落に分割してトーンの変化を検出
        drift_result = engine.detect_tone_drift(sample_article_with_tone)
        
        assert drift_result is not None
        assert "has_tone_drift" in drift_result
        assert "drift_locations" in drift_result
        assert "severity_score" in drift_result
        assert isinstance(drift_result["has_tone_drift"], bool)

    def test_formality_level_consistency_敬語レベル一貫性(self, sample_article_with_tone):
        """敬語・丁寧語レベルの一貫性をテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        formality_result = engine.check_formality_consistency(sample_article_with_tone)
        
        assert formality_result is not None
        assert "formality_score" in formality_result
        assert "inconsistent_patterns" in formality_result
        assert "recommended_level" in formality_result
        assert 0.0 <= formality_result["formality_score"] <= 1.0

    def test_emotional_tone_analysis_感情トーン分析(self, sample_article_with_tone):
        """感情トーンの分析と一貫性チェックをテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        emotion_result = engine.analyze_emotional_tone(sample_article_with_tone)
        
        assert emotion_result is not None
        assert "dominant_emotion" in emotion_result
        assert "emotion_consistency" in emotion_result
        assert "emotion_distribution" in emotion_result
        assert isinstance(emotion_result["emotion_consistency"], (int, float))

    def test_audience_alignment_check_読者層適合性チェック(self, sample_article_with_tone):
        """読者層との適合性をテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        alignment_result = engine.check_audience_alignment(sample_article_with_tone)
        
        assert alignment_result is not None
        assert "alignment_score" in alignment_result
        assert "misalignment_issues" in alignment_result
        assert "recommendations" in alignment_result
        assert 0.0 <= alignment_result["alignment_score"] <= 1.0

    def test_generate_improvement_suggestions_改善提案生成(self, inconsistent_article, brand_guidelines):
        """改善提案生成機能をテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        suggestions = engine.generate_improvement_suggestions(
            inconsistent_article,
            brand_guidelines
        )
        
        assert suggestions is not None
        assert "priority_issues" in suggestions
        assert "specific_recommendations" in suggestions
        assert "revised_sentences" in suggestions
        assert isinstance(suggestions["priority_issues"], list)
        assert len(suggestions["specific_recommendations"]) > 0

    def test_bulk_consistency_analysis_一括一貫性分析(self, sample_article_with_tone, inconsistent_article):
        """複数記事の一括一貫性分析をテスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        articles = [sample_article_with_tone, inconsistent_article]
        
        bulk_result = engine.analyze_bulk_consistency(articles)
        
        assert bulk_result is not None
        assert "overall_consistency" in bulk_result
        assert "article_scores" in bulk_result
        assert "common_issues" in bulk_result
        assert len(bulk_result["article_scores"]) == 2

    def test_validation_and_error_handling_バリデーション(self):
        """入力バリデーションとエラーハンドリング"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        
        engine = ToneMannnerEngine()
        
        # 空のコンテンツに対するエラーハンドリング
        with pytest.raises(ValueError, match="Article content is required"):
            engine.check_writing_consistency({"content": ""})
        
        # 不正なトーンプロファイルに対するエラーハンドリング
        with pytest.raises(ValueError, match="Tone profile is required"):
            engine.check_writing_consistency({"content": "test content"})

    def test_performance_benchmarks_パフォーマンス(self, sample_article_with_tone):
        """パフォーマンステスト"""
        from src.content.tone_manner_engine import ToneMannnerEngine
        import time
        
        engine = ToneMannnerEngine()
        
        # 一貫性チェックのパフォーマンステスト
        large_content_article = sample_article_with_tone.copy()
        large_content_article["content"] = "これはパフォーマンステスト用の長いコンテンツです。" * 1000
        
        start_time = time.time()
        result = engine.check_writing_consistency(large_content_article)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 10.0, f"Consistency check took {execution_time} seconds, should be under 10 seconds"
        assert result is not None