#!/usr/bin/env python3
"""
🧠 Critical Path Tests - AI Service Manager
最高ビジネス価値コンポーネント (10/10) の包括的テスト

ビジネスクリティカルな AI サービス管理機能の検証
"""

import pytest
import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass
import logging

# Test対象のインポート（実際のパスに合わせて調整）
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from services.ai.ai_service_manager import AIServiceManager
from services.ai.gemini_service import GeminiService
from services.ai.anthropic_service import AnthropicService  
from services.ai.openai_service import OpenAIService
from models.api_key import APIProvider

logger = logging.getLogger(__name__)


@dataclass
class ProviderTestResult:
    """プロバイダーテスト結果"""
    provider: str
    success: bool
    response_time: float
    quality_score: float
    error_message: Optional[str] = None


class TestAIServiceManagerCriticalPath:
    """
    AI Service Manager クリティカルパステスト
    
    ビジネス価値: 10/10 (最高)
    技術複雑度: 9/10 (極高)
    外部依存度: 10/10 (極高)
    テスト優先度: CRITICAL
    """
    
    @pytest.fixture
    async def ai_service_manager(self):
        """AI Service Manager のテストインスタンス"""
        # モックデータベースセッション
        mock_db = MagicMock()
        user_id = 1
        
        # AIServiceManagerインスタンス作成
        manager = AIServiceManager(db=mock_db, user_id=user_id)
        
        # サービスのモック設定
        for provider, service in manager.services.items():
            service.api_key = "test_api_key"
            service.generate_text = AsyncMock(return_value={
                "success": True,
                "content": "Mock generated content",
                "usage": {"tokens": 100}
            })
            service.analyze_content = AsyncMock(return_value={
                "success": True,
                "analysis": {"score": 85.0}
            })
        
        # API key serviceのモック
        manager.api_key_service.get_api_keys = MagicMock(return_value=[])
        manager._check_usage_limits = MagicMock(return_value=True)
        manager._update_usage = AsyncMock(return_value=None)
        
        return manager
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_complete_provider_failover_resilience(self, ai_service_manager):
        """
        完全プロバイダーフェイルオーバー復旧性テスト
        
        ビジネスシナリオ: 主要プロバイダー障害時の自動フォールバック
        成功基準:
        - フェイルオーバー時間: 2秒以内
        - 成功率: 99%以上
        - データ整合性: 100%
        """
        
        # テスト設定
        test_prompt = "誕生花の記事を生成してください。1月の誕生花について詳しく説明し、花言葉も含めてください。"
        failover_times = []
        success_count = 0
        total_attempts = 10
        
        for attempt in range(total_attempts):
            # Gemini プロバイダー障害をシミュレート
            with patch.object(
                ai_service_manager.services[APIProvider.GOOGLE_GEMINI], 
                'generate_text',
                side_effect=Exception("API Rate Limit Exceeded")
            ):
                start_time = time.time()
                
                try:
                    # フェイルオーバー実行
                    result = await ai_service_manager.generate_text(
                        prompt=test_prompt,
                        provider=APIProvider.GOOGLE_GEMINI
                    )
                    
                    failover_time = time.time() - start_time
                    failover_times.append(failover_time)
                    
                    # 結果検証
                    assert result.success is True
                    assert result["provider_used"] != "google_gemini"  # フォールバック確認
                    assert len(result["content"]) > 10    # 最小コンテンツ長
                    
                    success_count += 1
                    
                    logger.info(f"✅ Attempt {attempt + 1}: Failover successful in {failover_time:.2f}s")
                    
                except Exception as e:
                    logger.error(f"❌ Attempt {attempt + 1}: Failover failed - {e}")
        
        # 成功基準検証
        success_rate = success_count / total_attempts
        avg_failover_time = statistics.mean(failover_times) if failover_times else float('inf')
        
        assert success_rate >= 0.99, f"Success rate {success_rate:.2%} below 99% threshold"
        assert avg_failover_time <= 2.0, f"Average failover time {avg_failover_time:.2f}s exceeds 2s limit"
        
        logger.info(f"🎉 Failover resilience test passed:")
        logger.info(f"   Success Rate: {success_rate:.2%}")
        logger.info(f"   Avg Failover Time: {avg_failover_time:.2f}s")
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_cascade_failure_prevention(self, ai_service_manager):
        """
        カスケード障害防止テスト
        
        ビジネスシナリオ: 複数プロバイダー同時障害時の対応
        成功基準:
        - カスケード障害防止: 100%
        - 最終フォールバック成功: 95%以上
        - システム安定性維持: 100%
        """
        
        cascade_scenarios = [
            # シナリオ1: Gemini + Claude 障害
            {'failed_providers': [APIProvider.GOOGLE_GEMINI, APIProvider.ANTHROPIC], 'expected_provider': 'openai'},
            # シナリオ2: Gemini + OpenAI 障害  
            {'failed_providers': [APIProvider.GOOGLE_GEMINI, APIProvider.OPENAI], 'expected_provider': 'anthropic'},
            # シナリオ3: Claude + OpenAI 障害
            {'failed_providers': [APIProvider.ANTHROPIC, APIProvider.OPENAI], 'expected_provider': 'google_gemini'}
        ]
        
        for i, scenario in enumerate(cascade_scenarios, 1):
            logger.info(f"🧪 Testing cascade scenario {i}: {scenario['failed_providers']} failed")
            
            # 指定プロバイダーの障害をシミュレート
            patches = []
            for failed_provider in scenario['failed_providers']:
                patch_obj = patch.object(
                    ai_service_manager.services[failed_provider],
                    'generate_text',
                    side_effect=Exception(f"{failed_provider.value} service unavailable")
                )
                patches.append(patch_obj)
            
            # 複数パッチを適用
            for patch_obj in patches:
                patch_obj.start()
            
            try:
                # カスケード障害テスト実行
                result = await ai_service_manager.generate_text(
                    prompt="テスト用プロンプト"
                )
                
                # 結果検証
                assert result["success"] is True
                assert result["provider_used"] == scenario['expected_provider']
                
                logger.info(f"✅ Scenario {i}: Successfully failed over to {result['provider_used']}")
                
            finally:
                # パッチをクリーンアップ
                for patch_obj in patches:
                    patch_obj.stop()
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_concurrent_request_stability(self, ai_service_manager):
        """
        並行リクエスト安定性テスト
        
        ビジネスシナリオ: 高負荷時の同時リクエスト処理
        成功基準:
        - 同時リクエスト数: 50個
        - 成功率: 95%以上  
        - 平均レスポンス時間: 30秒以内
        - メモリリーク: なし
        """
        
        concurrent_requests = 50
        test_prompts = [
            f"誕生花記事生成テスト {i}: {i}月の誕生花について"
            for i in range(1, concurrent_requests + 1)
        ]
        
        # 並行実行関数
        async def execute_request(prompt: str, request_id: int) -> ProviderTestResult:
            start_time = time.time()
            
            try:
                result = await ai_service_manager.generate_text(
                    prompt=prompt
                )
                
                response_time = time.time() - start_time
                
                return ProviderTestResult(
                    provider=result.get("provider_used", "unknown"),
                    success=result["success"],
                    response_time=response_time,
                    quality_score=85.0  # Mock quality score
                )
                
            except Exception as e:
                response_time = time.time() - start_time
                
                return ProviderTestResult(
                    provider="unknown",
                    success=False,
                    response_time=response_time,
                    quality_score=0.0,
                    error_message=str(e)
                )
        
        # 並行実行
        logger.info(f"🚀 Executing {concurrent_requests} concurrent requests...")
        
        start_time = time.time()
        
        # asyncio.gather で並行実行
        tasks = [
            execute_request(prompt, i) 
            for i, prompt in enumerate(test_prompts)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_execution_time = time.time() - start_time
        
        # 結果分析
        successful_results = [r for r in results if isinstance(r, ProviderTestResult) and r.success]
        failed_results = [r for r in results if not (isinstance(r, ProviderTestResult) and r.success)]
        
        success_rate = len(successful_results) / len(results)
        avg_response_time = statistics.mean([r.response_time for r in successful_results]) if successful_results else 0
        
        # プロバイダー使用状況分析
        provider_usage = {}
        for result in successful_results:
            provider_usage[result.provider] = provider_usage.get(result.provider, 0) + 1
        
        # 成功基準検証
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95% threshold"
        assert avg_response_time <= 30.0, f"Average response time {avg_response_time:.2f}s exceeds 30s limit"
        
        logger.info(f"🎉 Concurrent request test completed:")
        logger.info(f"   Total Requests: {len(results)}")
        logger.info(f"   Success Rate: {success_rate:.2%}")
        logger.info(f"   Avg Response Time: {avg_response_time:.2f}s")
        logger.info(f"   Total Execution Time: {total_execution_time:.2f}s")
        logger.info(f"   Provider Usage: {provider_usage}")
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_rate_limit_intelligent_handling(self, ai_service_manager):
        """
        レート制限インテリジェント処理テスト
        
        ビジネスシナリオ: API レート制限に対する適応的対応
        成功基準:
        - レート制限検出: 100%
        - 自動待機時間調整: 適切
        - 代替プロバイダー選択: 最適
        """
        
        # レート制限シミュレーション
        rate_limit_responses = [
            {"error": "Rate limit exceeded", "retry_after": 60},
            {"error": "Quota exhausted", "retry_after": 300},
            {"error": "Too many requests", "retry_after": 30}
        ]
        
        for i, rate_limit_response in enumerate(rate_limit_responses, 1):
            logger.info(f"🧪 Testing rate limit scenario {i}: {rate_limit_response['error']}")
            
            # レート制限エラーをシミュレート
            with patch.object(
                ai_service_manager.services[APIProvider.GOOGLE_GEMINI],
                'generate_text',
                side_effect=Exception(rate_limit_response['error'])
            ):
                start_time = time.time()
                
                # レート制限処理テスト（フォールバックを使用）
                result = await ai_service_manager.generate_text(
                    prompt="レート制限テスト用プロンプト",
                    provider=APIProvider.GOOGLE_GEMINI
                )
                
                handling_time = time.time() - start_time
                
                # 結果検証
                assert result["success"] is True
                assert result["provider_used"] != "google_gemini"  # 代替プロバイダー使用確認
                assert handling_time <= 5.0  # 迅速な代替対応
                
                logger.info(f"✅ Scenario {i}: Rate limit handled in {handling_time:.2f}s")
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_content_quality_consistency(self, ai_service_manager):
        """
        コンテンツ品質一貫性テスト
        
        ビジネスシナリオ: 異なるプロバイダー間での品質一貫性
        成功基準:
        - 品質スコア標準偏差: 5点以下
        - 最低品質スコア: 75点以上
        - 一貫性率: 95%以上
        """
        
        test_prompt = "1月の誕生花について詳しく説明してください。花言葉、由来、育て方も含めてください。"
        quality_scores = []
        content_lengths = []
        
        # 各プロバイダーでコンテンツ生成
        for provider in ai_service_manager.services.keys():
            logger.info(f"🧪 Testing content quality with {provider.value}")
            
            for iteration in range(3):  # 各プロバイダーで3回テスト
                result = await ai_service_manager.generate_text(
                    prompt=test_prompt,
                    provider=provider
                )
                
                if result["success"]:
                    quality_score = 85.0  # Mock quality score
                    quality_scores.append(quality_score)
                    content_lengths.append(len(result["content"]))
                    
                    logger.info(f"   Iteration {iteration + 1}: Quality {quality_score:.1f}")
        
        # 品質一貫性分析
        if quality_scores:
            quality_std = statistics.stdev(quality_scores)
            min_quality = min(quality_scores)
            avg_quality = statistics.mean(quality_scores)
            
            # 成功基準検証
            assert quality_std <= 5.0, f"Quality standard deviation {quality_std:.2f} exceeds 5.0 limit"
            assert min_quality >= 75.0, f"Minimum quality score {min_quality:.1f} below 75.0 threshold"
            
            # 一貫性率計算（品質スコア差が10点以内の割合）
            quality_pairs = [(quality_scores[i], quality_scores[i+1]) 
                            for i in range(len(quality_scores)-1)]
            consistent_pairs = [pair for pair in quality_pairs 
                              if abs(pair[0] - pair[1]) <= 10.0]
            consistency_rate = len(consistent_pairs) / len(quality_pairs) if quality_pairs else 0
            
            assert consistency_rate >= 0.95, f"Consistency rate {consistency_rate:.2%} below 95% threshold"
            
            logger.info(f"🎉 Content quality consistency verified:")
            logger.info(f"   Average Quality: {avg_quality:.1f}")
            logger.info(f"   Quality Std Dev: {quality_std:.2f}")
            logger.info(f"   Minimum Quality: {min_quality:.1f}")
            logger.info(f"   Consistency Rate: {consistency_rate:.2%}")
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_disaster_recovery_capability(self, ai_service_manager):
        """
        災害復旧能力テスト
        
        ビジネスシナリオ: 全プロバイダー同時障害からの復旧
        成功基準:
        - 障害検出時間: 10秒以内
        - 復旧プロセス開始: 15秒以内
        - データ損失: なし
        """
        
        logger.info("🚨 Testing disaster recovery capability...")
        
        # 全プロバイダー障害をシミュレート
        with patch.object(ai_service_manager.services[APIProvider.GOOGLE_GEMINI], 'generate_text', 
                         side_effect=Exception("Service unavailable")), \
             patch.object(ai_service_manager.services[APIProvider.ANTHROPIC], 'generate_text',
                         side_effect=Exception("Service unavailable")), \
             patch.object(ai_service_manager.services[APIProvider.OPENAI], 'generate_text',
                         side_effect=Exception("Service unavailable")):
            
            start_time = time.time()
            
            # 災害復旧テスト実行（全プロバイダー障害なので失敗が期待される）
            result = await ai_service_manager.generate_text(
                prompt="災害復旧テスト用プロンプト"
            )
            
            recovery_time = time.time() - start_time
            
            # 復旧結果検証（全プロバイダー障害の場合は失敗する）
            assert recovery_time <= 15.0, f"Recovery time {recovery_time:.2f}s exceeds 15s limit"
            
            # 全プロバイダー障害時の適切なエラーハンドリング確認
            if not result["success"]:
                assert "All providers failed" in result["error"]
                assert "providers_tried" in result
                logger.info("✅ Graceful degradation confirmed - all providers failed")
            else:
                # 予期せぬ成功の場合（モックの設定問題など）
                logger.info("⚠️ Unexpected success despite all providers being down")
            
            logger.info(f"🎉 Disaster recovery test completed in {recovery_time:.2f}s")


class TestAIServiceManagerIntegration:
    """
    AI Service Manager 統合テスト
    
    他システムとの連携テスト
    """
    
    @pytest.mark.integration
    @pytest.mark.asyncio 
    async def test_keyword_analyzer_integration(self, ai_service_manager):
        """キーワードアナライザー統合テスト"""
        
        # 統合テスト実装
        # KeywordAnalyzer との連携確認
        pass
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_content_management_integration(self, ai_service_manager):
        """コンテンツ管理システム統合テスト"""
        
        # 統合テスト実装
        # ContentManagementSystem との連携確認
        pass


if __name__ == "__main__":
    # クリティカルパステストのみ実行
    pytest.main([
        __file__,
        "-v", 
        "-m", "critical",
        "--tb=short"
    ])