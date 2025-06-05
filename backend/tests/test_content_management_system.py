"""
Test for Content Management System
コンテンツ管理システムのテスト
TDD Red Phase: テスト作成
"""
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from datetime import datetime


@pytest.fixture
def sample_article_content():
    """サンプル記事コンテンツ"""
    return {
        "id": "article_001",
        "title": "3月の誕生花チューリップの花言葉と魅力",
        "content": """
        3月の誕生花であるチューリップは、春の訪れを告げる美しい花として親しまれています。
        その鮮やかな色彩と優雅な形状で、多くの人々に愛され続けています。
        チューリップの花言葉は「思いやり」「美しい眼差し」「正直」などがあります。
        """,
        "primary_keyword": "3月 誕生花",
        "secondary_keywords": ["チューリップ", "花言葉"],
        "created_at": datetime.now(),
        "user_id": "user_001",
        "tone_manner_profile": {
            "writing_style": "親しみやすく丁寧",
            "target_audience": "一般読者",
            "brand_voice": "専門的だが分かりやすい"
        }
    }


@pytest.fixture
def duplicate_article_content():
    """重複検出用のサンプル記事コンテンツ"""
    return {
        "id": "article_002",
        "title": "3月の誕生花チューリップについて詳しく解説",
        "content": """
        3月の誕生花チューリップは、春を代表する美しい花です。
        その鮮やかな色合いと上品な形で、多くの人に愛されています。
        チューリップの花言葉には「思いやり」「美しい眼差し」などがあります。
        """,
        "primary_keyword": "3月 誕生花",
        "secondary_keywords": ["チューリップ", "花言葉"],
        "created_at": datetime.now(),
        "user_id": "user_001"
    }


class TestContentManagementSystem:
    """コンテンツ管理システムのテストクラス"""

    def test_save_article_content_記事保存機能(self, sample_article_content):
        """記事コンテンツの保存機能をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        result = cms.save_article(sample_article_content)
        
        assert result is not None
        assert result["status"] == "saved"
        assert result["article_id"] == sample_article_content["id"]
        assert "fingerprint" in result
        assert "tone_profile" in result

    def test_content_fingerprinting_コンテンツフィンガープリンティング(self, sample_article_content):
        """コンテンツのフィンガープリンティング機能をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        fingerprint = cms.generate_content_fingerprint(sample_article_content["content"])
        
        assert fingerprint is not None
        assert isinstance(fingerprint, str)
        assert len(fingerprint) > 0
        
        # 同じコンテンツは同じフィンガープリントを生成
        fingerprint2 = cms.generate_content_fingerprint(sample_article_content["content"])
        assert fingerprint == fingerprint2

    def test_duplicate_detection_重複検出機能(self, sample_article_content, duplicate_article_content):
        """重複コンテンツ検出機能をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        # 最初の記事を保存
        cms.save_article(sample_article_content)
        
        # 重複検出を実行
        duplicate_result = cms.detect_duplicates(duplicate_article_content)
        
        assert duplicate_result is not None
        assert "is_duplicate" in duplicate_result
        assert "similarity_score" in duplicate_result
        assert duplicate_result["similarity_score"] > 0.4  # 40%以上の類似度（実用的な閾値）
        assert duplicate_result["is_duplicate"] is True

    def test_similarity_scoring_類似度計算(self, sample_article_content, duplicate_article_content):
        """コンテンツ類似度スコア計算をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        content1 = sample_article_content["content"]
        content2 = duplicate_article_content["content"]
        
        similarity_score = cms.calculate_similarity(content1, content2)
        
        assert 0.0 <= similarity_score <= 1.0
        assert similarity_score > 0.4  # 適度な類似度を期待

    def test_cosine_similarity_コサイン類似度(self):
        """コサイン類似度アルゴリズムをテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        # 同じテキスト
        text1 = "これはテストのための文章です"
        text2 = "これはテストのための文章です"
        
        similarity = cms.calculate_cosine_similarity(text1, text2)
        assert similarity == 1.0  # 完全一致
        
        # 異なるテキスト
        text3 = "まったく異なる内容の文章を作成しました"
        similarity2 = cms.calculate_cosine_similarity(text1, text3)
        assert 0.0 <= similarity2 < 1.0

    def test_duplicate_alert_system_重複アラート(self, sample_article_content, duplicate_article_content):
        """重複アラートシステムをテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        # 閾値設定（現実的な値に調整）
        cms.set_duplicate_threshold(0.3)
        
        # 最初の記事を保存
        cms.save_article(sample_article_content)
        
        # 重複アラートをチェック
        alert_result = cms.check_duplicate_alert(duplicate_article_content)
        
        assert alert_result is not None
        assert "alert_triggered" in alert_result
        assert "threshold_exceeded" in alert_result
        assert "similar_articles" in alert_result
        assert alert_result["alert_triggered"] is True

    def test_content_versioning_バージョン管理(self, sample_article_content):
        """コンテンツのバージョン管理をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        # 初回保存
        result1 = cms.save_article(sample_article_content)
        
        # 同じIDで更新
        updated_content = sample_article_content.copy()
        updated_content["content"] = "更新されたコンテンツです。新しい情報を追加しました。"
        
        result2 = cms.save_article(updated_content)
        
        assert result1["version"] == 1
        assert result2["version"] == 2
        
        # バージョン履歴を取得
        versions = cms.get_article_versions(sample_article_content["id"])
        assert len(versions) == 2

    def test_tone_manner_preservation_トンマナ保存(self, sample_article_content):
        """トーン&マナー情報の保存をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        result = cms.save_article(sample_article_content)
        
        # トーン&マナー情報が保存されていることを確認
        assert "tone_profile" in result
        stored_article = cms.get_article(sample_article_content["id"])
        assert stored_article["tone_manner_profile"] == sample_article_content["tone_manner_profile"]

    def test_search_similar_articles_類似記事検索(self, sample_article_content):
        """類似記事検索機能をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        # 複数記事を保存
        cms.save_article(sample_article_content)
        
        # 検索クエリ
        search_query = "チューリップ 花言葉"
        
        similar_articles = cms.search_similar_articles(search_query, threshold=0.5)
        
        assert isinstance(similar_articles, list)
        assert len(similar_articles) > 0
        assert all("similarity_score" in article for article in similar_articles)

    def test_content_cleanup_コンテンツクリーンアップ(self, sample_article_content):
        """コンテンツのクリーンアップ機能をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        raw_content = """
        
        これは  不要な   スペースや

        改行が    含まれた  コンテンツです。
        
        
        """
        
        cleaned_content = cms.clean_content(raw_content)
        
        # 余分な空白や改行が除去されていることを確認
        assert "これは不要なスペースや" in cleaned_content
        assert "  " not in cleaned_content  # 連続スペースが除去されている
        assert not cleaned_content.startswith("\n")  # 先頭の改行が除去されている

    def test_batch_duplicate_check_一括重複チェック(self, sample_article_content):
        """一括重複チェック機能をテスト"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        # 複数記事をリストで準備
        articles = [
            sample_article_content,
            {
                "id": "article_002",
                "content": "全く異なる内容の記事です。重複しないはずです。",
                "title": "異なる記事"
            },
            {
                "id": "article_003", 
                "content": sample_article_content["content"],  # 重複コンテンツ
                "title": "重複記事"
            }
        ]
        
        duplicate_report = cms.batch_duplicate_check(articles)
        
        assert "total_articles" in duplicate_report
        assert "duplicate_pairs" in duplicate_report
        assert duplicate_report["total_articles"] == 3
        assert len(duplicate_report["duplicate_pairs"]) > 0

    def test_validation_and_error_handling_バリデーション(self):
        """入力バリデーションとエラーハンドリング"""
        from src.content.content_management_system import ContentManagementSystem
        
        cms = ContentManagementSystem()
        
        # 空のコンテンツに対するエラーハンドリング
        with pytest.raises(ValueError, match="Content is required"):
            cms.save_article({"id": "test", "content": ""})
        
        # 不正な記事IDに対するエラーハンドリング
        with pytest.raises(ValueError, match="Article ID is required"):
            cms.save_article({"content": "test content"})

    def test_performance_benchmarks_パフォーマンス(self, sample_article_content):
        """パフォーマンステスト"""
        from src.content.content_management_system import ContentManagementSystem
        import time
        
        cms = ContentManagementSystem()
        
        # 類似度計算のパフォーマンステスト
        large_content = "これはパフォーマンステスト用の長いコンテンツです。" * 1000
        
        start_time = time.time()
        fingerprint = cms.generate_content_fingerprint(large_content)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0, f"Fingerprint generation took {execution_time} seconds, should be under 5 seconds"
        assert fingerprint is not None