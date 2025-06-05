"""
Test for Fact Checking System
ファクトチェック・品質担保機能のテスト
TDD Red Phase: ファクトチェック機能のテスト作成
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from datetime import datetime


@pytest.fixture
def sample_article_with_facts():
    """事実情報を含むサンプル記事"""
    return {
        "id": "article_001",
        "title": "3月の誕生花チューリップの花言葉",
        "content": """
        3月の誕生花はチューリップです。チューリップの原産地はトルコで、
        16世紀にヨーロッパに伝わりました。花言葉は「思いやり」「美しい眼差し」です。
        チューリップは春の代表的な花として、世界中で愛されています。
        オランダは世界最大のチューリップ生産国で、年間約30億本を生産しています。
        """,
        "factual_claims": [
            {"claim": "3月の誕生花はチューリップ", "type": "birth_flower"},
            {"claim": "チューリップの原産地はトルコ", "type": "origin"},
            {"claim": "16世紀にヨーロッパに伝わった", "type": "historical"},
            {"claim": "オランダは世界最大のチューリップ生産国", "type": "production"},
            {"claim": "年間約30億本を生産", "type": "statistics"}
        ],
        "sources": [
            "植物百科事典",
            "園芸学会資料",
            "国際花卉統計"
        ]
    }


@pytest.fixture
def questionable_article():
    """疑わしい情報を含む記事サンプル"""
    return {
        "id": "article_002",
        "title": "驚異的な効果を持つ奇跡の花",
        "content": """
        この花を1日見るだけで必ず健康になります。
        科学的に100%証明された効果があり、絶対に病気が治ります。
        世界中の医師が推奨する最強の治療法です。
        副作用は一切なく、誰でも安全に使用できます。
        """,
        "factual_claims": [
            {"claim": "1日見るだけで必ず健康になる", "type": "health_claim"},
            {"claim": "科学的に100%証明された", "type": "scientific_claim"},
            {"claim": "絶対に病気が治る", "type": "medical_claim"},
            {"claim": "世界中の医師が推奨", "type": "authority_claim"}
        ]
    }


@pytest.fixture
def trusted_sources():
    """信頼できる情報源のデータ"""
    return {
        "botanical_databases": [
            "Royal Horticultural Society",
            "Kew Gardens Database",
            "植物百科事典"
        ],
        "academic_sources": [
            "園芸学会",
            "植物学会",
            "国際花卉研究所"
        ],
        "statistical_sources": [
            "国際花卉統計",
            "農林水産省統計",
            "オランダ花き協会"
        ],
        "blacklisted_indicators": [
            "必ず", "絶対に", "100%", "奇跡の",
            "世界中の医師", "副作用なし", "最強の"
        ]
    }


class TestFactCheckingSystem:
    """ファクトチェックシステムのテストクラス"""

    def test_verify_factual_claims_事実確認機能(self, sample_article_with_facts, trusted_sources):
        """事実確認機能をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem(trusted_sources)
        
        verification_result = fact_checker.verify_factual_claims(sample_article_with_facts)
        
        assert verification_result is not None
        assert "verified_claims" in verification_result
        assert "unverified_claims" in verification_result
        assert "verification_score" in verification_result
        assert 0.0 <= verification_result["verification_score"] <= 1.0

    def test_check_source_reliability_情報源信頼性チェック(self, sample_article_with_facts, trusted_sources):
        """情報源の信頼性チェックをテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem(trusted_sources)
        
        reliability_result = fact_checker.check_source_reliability(sample_article_with_facts["sources"])
        
        assert reliability_result is not None
        assert "reliable_sources" in reliability_result
        assert "unreliable_sources" in reliability_result
        assert "reliability_score" in reliability_result
        assert isinstance(reliability_result["reliable_sources"], list)

    def test_detect_misinformation_patterns_誤情報パターン検出(self, questionable_article, trusted_sources):
        """誤情報パターンの検出をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem(trusted_sources)
        
        misinformation_result = fact_checker.detect_misinformation_patterns(questionable_article)
        
        assert misinformation_result is not None
        assert "risk_indicators" in misinformation_result
        assert "severity_level" in misinformation_result
        assert "flagged_content" in misinformation_result
        assert len(misinformation_result["risk_indicators"]) > 0

    def test_cross_reference_with_databases_データベース照合(self, sample_article_with_facts):
        """データベースとの照合機能をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        # モックデータベース応答
        with patch.object(fact_checker, '_query_botanical_database') as mock_db:
            mock_db.return_value = {
                "3月の誕生花はチューリップ": {"verified": True, "confidence": 0.9},
                "チューリップの原産地はトルコ": {"verified": True, "confidence": 0.8}
            }
            
            cross_ref_result = fact_checker.cross_reference_with_databases(
                sample_article_with_facts["factual_claims"]
            )
            
            assert cross_ref_result is not None
            assert "database_matches" in cross_ref_result
            assert "confidence_scores" in cross_ref_result

    def test_generate_quality_score_品質スコア生成(self, sample_article_with_facts, questionable_article):
        """品質スコア算出をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        # 良質な記事のスコア
        good_score = fact_checker.generate_quality_score(sample_article_with_facts)
        
        # 疑わしい記事のスコア
        poor_score = fact_checker.generate_quality_score(questionable_article)
        
        assert good_score is not None
        assert poor_score is not None
        assert "overall_score" in good_score
        assert "overall_score" in poor_score
        assert good_score["overall_score"] > poor_score["overall_score"]

    def test_identify_unsupported_claims_根拠不十分な主張の特定(self, sample_article_with_facts):
        """根拠が不十分な主張の特定をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        unsupported_result = fact_checker.identify_unsupported_claims(sample_article_with_facts)
        
        assert unsupported_result is not None
        assert "unsupported_claims" in unsupported_result
        assert "evidence_level" in unsupported_result
        assert "recommendations" in unsupported_result

    def test_check_statistical_accuracy_統計情報の正確性チェック(self, sample_article_with_facts):
        """統計情報の正確性チェックをテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        stats_check = fact_checker.check_statistical_accuracy(sample_article_with_facts)
        
        assert stats_check is not None
        assert "statistical_claims" in stats_check
        assert "accuracy_assessment" in stats_check
        assert "data_sources" in stats_check

    def test_flag_health_medical_claims_健康医療系主張のフラグ(self, questionable_article):
        """健康・医療系の主張のフラグ機能をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        health_flags = fact_checker.flag_health_medical_claims(questionable_article)
        
        assert health_flags is not None
        assert "flagged_claims" in health_flags
        assert "risk_level" in health_flags
        assert "requires_disclaimer" in health_flags
        assert len(health_flags["flagged_claims"]) > 0

    def test_generate_fact_check_report_ファクトチェックレポート生成(self, sample_article_with_facts):
        """ファクトチェックレポート生成をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        report = fact_checker.generate_fact_check_report(sample_article_with_facts)
        
        assert report is not None
        assert "article_id" in report
        assert "verification_summary" in report
        assert "source_assessment" in report
        assert "quality_metrics" in report
        assert "recommendations" in report
        assert "generated_at" in report

    def test_batch_fact_checking_一括ファクトチェック(self, sample_article_with_facts, questionable_article):
        """複数記事の一括ファクトチェックをテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        articles = [sample_article_with_facts, questionable_article]
        
        batch_result = fact_checker.batch_fact_checking(articles)
        
        assert batch_result is not None
        assert "total_articles" in batch_result
        assert "summary_stats" in batch_result
        assert "flagged_articles" in batch_result
        assert len(batch_result["summary_stats"]) == 2

    def test_continuous_monitoring_継続監視機能(self, sample_article_with_facts):
        """継続的な監視機能をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        monitoring_setup = fact_checker.setup_continuous_monitoring(
            sample_article_with_facts,
            check_interval=24  # 24時間ごと
        )
        
        assert monitoring_setup is not None
        assert "monitoring_id" in monitoring_setup
        assert "next_check" in monitoring_setup
        assert "monitoring_parameters" in monitoring_setup

    @pytest.mark.asyncio
    async def test_async_external_verification_外部検証(self, sample_article_with_facts):
        """外部APIを使用した非同期検証をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        # 外部API呼び出しをモック
        with patch.object(fact_checker, '_call_external_fact_check_api') as mock_api:
            mock_api.return_value = AsyncMock(return_value={
                "verification_status": "verified",
                "confidence": 0.85,
                "sources": ["external_db_1", "external_db_2"]
            })
            
            external_result = await fact_checker.verify_with_external_apis(
                sample_article_with_facts["factual_claims"]
            )
            
            assert external_result is not None
            assert "external_verification" in external_result
            assert "api_responses" in external_result

    def test_validate_citations_引用検証(self, sample_article_with_facts):
        """引用の検証をテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        citation_result = fact_checker.validate_citations(sample_article_with_facts)
        
        assert citation_result is not None
        assert "valid_citations" in citation_result
        assert "missing_citations" in citation_result
        assert "citation_quality" in citation_result

    def test_temporal_fact_checking_時系列ファクトチェック(self, sample_article_with_facts):
        """時系列データのファクトチェックをテスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        temporal_result = fact_checker.check_temporal_accuracy(sample_article_with_facts)
        
        assert temporal_result is not None
        assert "date_claims" in temporal_result
        assert "chronological_accuracy" in temporal_result
        assert "outdated_information" in temporal_result

    def test_validation_and_error_handling_バリデーション(self):
        """入力バリデーションとエラーハンドリング"""
        from src.content.fact_checking_system import FactCheckingSystem
        
        fact_checker = FactCheckingSystem()
        
        # 空のコンテンツに対するエラーハンドリング
        with pytest.raises(ValueError, match="Article content is required"):
            fact_checker.verify_factual_claims({"content": ""})
        
        # 不正な記事構造に対するエラーハンドリング
        with pytest.raises(ValueError, match="Invalid article structure"):
            fact_checker.verify_factual_claims({})

    def test_performance_benchmarks_パフォーマンス(self, sample_article_with_facts):
        """パフォーマンステスト"""
        from src.content.fact_checking_system import FactCheckingSystem
        import time
        
        fact_checker = FactCheckingSystem()
        
        # ファクトチェックのパフォーマンステスト
        large_article = sample_article_with_facts.copy()
        large_article["content"] = large_article["content"] * 100  # 大きなコンテンツ
        large_article["factual_claims"] = sample_article_with_facts["factual_claims"] * 20
        
        start_time = time.time()
        result = fact_checker.verify_factual_claims(large_article)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 30.0, f"Fact checking took {execution_time} seconds, should be under 30 seconds"
        assert result is not None