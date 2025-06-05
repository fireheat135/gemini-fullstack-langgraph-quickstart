"""
Test for Meta Description Generator
メタディスクリプション生成機能のテスト
TDD Red Phase: テスト作成
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List


@pytest.fixture
def sample_article_context():
    """サンプル記事コンテキスト"""
    return {
        "title": "3月の誕生花チューリップの花言葉と魅力を徹底解説",
        "primary_keyword": "3月 誕生花",
        "secondary_keywords": ["チューリップ", "花言葉", "プレゼント"],
        "content_summary": "3月の誕生花であるチューリップの基本情報、花言葉の由来、プレゼントでの活用方法について詳しく解説する記事",
        "target_emotion": "知識欲の満足、学びの喜び",
        "call_to_action": "関連記事の閲覧",
        "tone": "親しみやすく、専門的"
    }


@pytest.fixture
def meta_description_requirements():
    """メタディスクリプション要件"""
    return {
        "max_length": 160,
        "min_length": 120,
        "keyword_density_target": 0.02,  # 2%
        "emotional_words": ["魅力", "完全", "徹底", "詳しく", "おすすめ"],
        "action_words": ["解説", "紹介", "ガイド", "比較", "選び方"]
    }


class TestMetaDescriptionGenerator:
    """メタディスクリプション生成器のテストクラス"""

    def test_generate_meta_description_基本機能(self, sample_article_context):
        """基本的なメタディスクリプション生成機能のテスト"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        meta_description = generator.generate_meta_description(sample_article_context)
        
        assert meta_description is not None
        assert isinstance(meta_description, str)
        assert len(meta_description) <= 160
        assert len(meta_description) >= 120
        assert "3月" in meta_description
        assert "誕生花" in meta_description

    def test_character_limit_validation_文字数制限(self, sample_article_context):
        """160文字制限の厳密なチェック"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        meta_description = generator.generate_meta_description(sample_article_context)
        
        # 160文字以下であることを確認
        assert len(meta_description) <= 160, f"Generated meta description is {len(meta_description)} characters, exceeds 160 limit"
        
        # 120文字以上であることを確認（短すぎるのも良くない）
        assert len(meta_description) >= 120, f"Generated meta description is {len(meta_description)} characters, too short"

    def test_keyword_inclusion_キーワード含有(self, sample_article_context):
        """キーワードの適切な含有率チェック"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        meta_description = generator.generate_meta_description(sample_article_context)
        
        # プライマリキーワードが含まれていること
        primary_keyword = sample_article_context["primary_keyword"]
        assert primary_keyword in meta_description or all(word in meta_description for word in primary_keyword.split())
        
        # セカンダリキーワードの一部が含まれていること
        secondary_keywords = sample_article_context["secondary_keywords"]
        included_secondary = sum(1 for keyword in secondary_keywords if keyword in meta_description)
        assert included_secondary >= 1, "At least one secondary keyword should be included"

    def test_keyword_density_check_キーワード密度(self, sample_article_context, meta_description_requirements):
        """キーワード密度の適切性チェック"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        result = generator.generate_meta_description_with_analysis(sample_article_context)
        
        assert "meta_description" in result
        assert "keyword_analysis" in result
        
        keyword_analysis = result["keyword_analysis"]
        assert "density" in keyword_analysis
        assert "included_keywords" in keyword_analysis
        
        # キーワード密度が適切な範囲にあること（1-15%程度 - 短い文章では密度が高くなることを考慮）
        density = keyword_analysis["density"]
        assert 0.01 <= density <= 0.15, f"Keyword density {density} is outside acceptable range"

    def test_emotional_appeal_感情訴求(self, sample_article_context):
        """感情に訴える表現の含有チェック"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        result = generator.generate_meta_description_with_analysis(sample_article_context)
        
        meta_description = result["meta_description"]
        emotional_analysis = result.get("emotional_analysis", {})
        
        # 感情訴求語が含まれていることを確認
        emotional_words = ["魅力", "完全", "徹底", "詳しく", "おすすめ", "人気", "厳選"]
        found_emotional_words = [word for word in emotional_words if word in meta_description]
        assert len(found_emotional_words) >= 1, f"No emotional words found in: {meta_description}"

    def test_call_to_action_integration_CTA統合(self, sample_article_context):
        """コールトゥアクションの適切な統合"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        meta_description = generator.generate_meta_description(sample_article_context)
        
        # CTAの要素が含まれていること
        cta_indicators = ["解説", "紹介", "ガイド", "チェック", "確認", "詳細"]
        found_cta = [indicator for indicator in cta_indicators if indicator in meta_description]
        assert len(found_cta) >= 1, f"No CTA indicators found in: {meta_description}"

    @pytest.mark.asyncio
    async def test_ai_generated_meta_description_AI生成(self, sample_article_context):
        """AIを活用したメタディスクリプション生成"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        
        with patch('src.content.meta_description_generator.MetaDescriptionGenerator._call_ai_service') as mock_ai:
            mock_ai.return_value = "3月の誕生花チューリップの美しい花言葉と魅力を徹底解説。プレゼント選びに役立つ詳細情報とおすすめの贈り方まで、専門家が丁寧に紹介します。"
            
            result = await generator.generate_ai_enhanced_meta_description(sample_article_context)
            
            assert result is not None
            assert len(result) <= 160
            assert "3月" in result
            assert "誕生花" in result
            mock_ai.assert_called_once()

    def test_multiple_variations_generation_複数バリエーション(self, sample_article_context):
        """複数のメタディスクリプションバリエーション生成"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        variations = generator.generate_multiple_variations(sample_article_context, count=3)
        
        assert len(variations) == 3
        assert all(isinstance(desc, str) for desc in variations)
        assert all(len(desc) <= 160 for desc in variations)
        assert all(len(desc) >= 120 for desc in variations)
        
        # すべてのバリエーションが異なることを確認
        assert len(set(variations)) == 3, "All variations should be unique"

    def test_seo_optimization_analysis_SEO最適化分析(self, sample_article_context):
        """SEO最適化の分析機能"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        result = generator.analyze_seo_optimization(sample_article_context)
        
        assert "seo_score" in result
        assert "recommendations" in result
        assert "keyword_analysis" in result
        assert "length_analysis" in result
        
        seo_score = result["seo_score"]
        assert 0 <= seo_score <= 100, f"SEO score {seo_score} should be between 0 and 100"

    def test_template_based_generation_テンプレート生成(self, sample_article_context):
        """テンプレートベースの生成機能"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        
        # 情報提供型テンプレート
        info_template_result = generator.generate_from_template(
            sample_article_context, 
            template_type="informational"
        )
        assert len(info_template_result) <= 160
        
        # 問題解決型テンプレート
        problem_solving_result = generator.generate_from_template(
            sample_article_context, 
            template_type="problem_solving"
        )
        assert len(problem_solving_result) <= 160
        
        # 2つの結果が異なることを確認
        assert info_template_result != problem_solving_result

    def test_birth_flower_specific_optimization_誕生花特化最適化(self, sample_article_context):
        """誕生花記事特化のメタディスクリプション最適化"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        result = generator.generate_birth_flower_optimized(sample_article_context)
        
        assert "meta_description" in result
        assert "birth_flower_elements" in result
        
        meta_desc = result["meta_description"]
        elements = result["birth_flower_elements"]
        
        # 誕生花特有の要素が含まれていることを確認
        assert any(element in meta_desc for element in ["誕生花", "花言葉", "月"]), "Birth flower specific elements should be included"
        
        # 誕生花関連の情緒的表現が含まれていることを確認
        birth_flower_emotions = ["美しい", "意味", "特別", "魅力", "贈り物"]
        found_emotions = [emotion for emotion in birth_flower_emotions if emotion in meta_desc]
        assert len(found_emotions) >= 1, f"No birth flower emotional words found in: {meta_desc}"

    def test_validation_and_error_handling_バリデーション(self):
        """入力バリデーションとエラーハンドリング"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        
        generator = MetaDescriptionGenerator()
        
        # 空の入力に対するエラーハンドリング
        with pytest.raises(ValueError, match="Article context is required"):
            generator.generate_meta_description({})
        
        # 不正な入力に対するエラーハンドリング
        with pytest.raises(ValueError, match="Title is required"):
            generator.generate_meta_description({"primary_keyword": "test"})

    def test_performance_benchmarks_パフォーマンス(self, sample_article_context):
        """パフォーマンステスト"""
        from src.content.meta_description_generator import MetaDescriptionGenerator
        import time
        
        generator = MetaDescriptionGenerator()
        
        start_time = time.time()
        result = generator.generate_meta_description(sample_article_context)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 2.0, f"Meta description generation took {execution_time} seconds, should be under 2 seconds"
        assert result is not None