#!/usr/bin/env python3
"""
🧠 Critical Path Tests - Content Generation Engine  
コア機能 (ビジネス価値 9/10) の包括的品質検証

誕生花記事生成の品質・一貫性・SEO最適化テスト
"""

import pytest
import asyncio
import statistics
import time
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass
import logging
import re

# Test対象のインポート
from src.content.deep_research_content_generator import DeepResearchContentGenerator
from src.seo.keyword_analyzer import KeywordAnalyzer
from src.services.ai.ai_service_manager import AIServiceManager

logger = logging.getLogger(__name__)


@dataclass
class ContentQualityMetrics:
    """コンテンツ品質メトリクス"""
    overall_score: float
    readability_score: float
    seo_optimization_score: float
    factual_accuracy_score: float
    content_uniqueness_score: float
    keyword_density: Dict[str, float]
    content_length: int
    structure_score: float


@dataclass
class SEOAnalysisResult:
    """SEO分析結果"""
    title_optimization: float
    meta_description_score: float
    heading_structure_score: float
    keyword_distribution_score: float
    internal_link_opportunities: int
    content_depth_score: float


class TestContentGenerationEngineQuality:
    """
    Content Generation Engine 品質テスト
    
    ビジネス価値: 9/10 (コア機能)
    技術複雑度: 8/10 (高)
    外部依存度: 9/10 (極高)
    テスト優先度: CRITICAL
    """
    
    @pytest.fixture
    async def content_generator(self):
        """Content Generator のテストインスタンス"""
        generator = DeepResearchContentGenerator()
        
        # 依存関係のモック設定
        generator.ai_service_manager = AsyncMock(spec=AIServiceManager)
        generator.keyword_analyzer = AsyncMock(spec=KeywordAnalyzer)
        
        # AI サービスマネージャーのモック設定
        generator.ai_service_manager.generate_content_with_fallback.return_value = AsyncMock(
            success=True,
            content="Mock generated content about birth flowers...",
            provider="gemini",
            quality_score=85.0
        )
        
        return generator
    
    @pytest.fixture
    def birth_flower_test_data(self):
        """誕生花テストデータ"""
        return {
            "january": {
                "keywords": ["1月", "誕生花", "カーネーション", "花言葉", "スノードロップ"],
                "expected_elements": ["カーネーション", "スノードロップ", "花言葉", "育て方", "由来"],
                "seo_targets": {
                    "primary": "1月 誕生花",
                    "secondary": ["カーネーション 花言葉", "誕生花 1月生まれ", "1月 花"]
                }
            },
            "march": {
                "keywords": ["3月", "誕生花", "桜", "チューリップ", "花言葉"],
                "expected_elements": ["桜", "チューリップ", "花言葉", "開花時期", "品種"],
                "seo_targets": {
                    "primary": "3月 誕生花",
                    "secondary": ["桜 花言葉", "チューリップ 種類", "3月 花"]
                }
            }
        }
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_birth_flower_content_quality_consistency(self, content_generator, birth_flower_test_data):
        """
        誕生花コンテンツ品質一貫性テスト
        
        ビジネスシナリオ: 12ヶ月分の誕生花記事品質の一貫性確保
        成功基準:
        - 品質スコア標準偏差: 5点以下
        - 最低品質スコア: 80点以上
        - 一貫性率: 95%以上
        """
        
        logger.info("🌸 Testing birth flower content quality consistency...")
        
        quality_metrics = []
        generation_times = []
        
        # 複数月のテストデータで品質検証
        for month, test_data in birth_flower_test_data.items():
            logger.info(f"📝 Generating content for {month}...")
            
            start_time = time.time()
            
            # コンテンツ生成実行
            result = await content_generator.generate_birth_flower_article(
                month=month,
                target_keywords=test_data["keywords"],
                seo_targets=test_data["seo_targets"],
                quality_mode="high"
            )
            
            generation_time = time.time() - start_time
            generation_times.append(generation_time)
            
            # 品質メトリクス評価
            metrics = await self._evaluate_content_quality(
                content=result.content,
                expected_elements=test_data["expected_elements"],
                target_keywords=test_data["keywords"]
            )
            
            quality_metrics.append(metrics)
            
            logger.info(f"   Quality Score: {metrics.overall_score:.1f}")
            logger.info(f"   Generation Time: {generation_time:.2f}s")
        
        # 品質一貫性分析
        quality_scores = [m.overall_score for m in quality_metrics]
        
        if quality_scores:
            quality_std = statistics.stdev(quality_scores)
            min_quality = min(quality_scores)
            avg_quality = statistics.mean(quality_scores)
            
            # 成功基準検証
            assert quality_std <= 5.0, f"Quality std deviation {quality_std:.2f} exceeds 5.0 limit"
            assert min_quality >= 80.0, f"Minimum quality score {min_quality:.1f} below 80.0 threshold"
            
            # 一貫性率計算
            quality_pairs = [(quality_scores[i], quality_scores[i+1]) 
                            for i in range(len(quality_scores)-1)]
            consistent_pairs = [pair for pair in quality_pairs 
                              if abs(pair[0] - pair[1]) <= 8.0]
            consistency_rate = len(consistent_pairs) / len(quality_pairs) if quality_pairs else 1.0
            
            assert consistency_rate >= 0.95, f"Consistency rate {consistency_rate:.2%} below 95% threshold"
            
            logger.info(f"🎉 Content quality consistency verified:")
            logger.info(f"   Average Quality: {avg_quality:.1f}")
            logger.info(f"   Quality Std Dev: {quality_std:.2f}")
            logger.info(f"   Minimum Quality: {min_quality:.1f}")
            logger.info(f"   Consistency Rate: {consistency_rate:.2%}")
    
    async def _evaluate_content_quality(self, content: str, expected_elements: List[str], 
                                      target_keywords: List[str]) -> ContentQualityMetrics:
        """コンテンツ品質評価"""
        
        # 基本メトリクス
        content_length = len(content)
        word_count = len(content.split())
        
        # 可読性スコア（簡易実装）
        readability_score = await self._calculate_readability_score(content)
        
        # SEO最適化スコア
        seo_score = await self._calculate_seo_optimization_score(content, target_keywords)
        
        # 事実正確性スコア（要素の存在確認）
        factual_accuracy = self._calculate_factual_accuracy(content, expected_elements)
        
        # コンテンツ独自性スコア（簡易実装）
        uniqueness_score = await self._calculate_content_uniqueness(content)
        
        # キーワード密度
        keyword_density = self._calculate_keyword_density(content, target_keywords)
        
        # 構造スコア
        structure_score = self._calculate_structure_score(content)
        
        # 総合スコア計算
        overall_score = (
            readability_score * 0.25 +
            seo_score * 0.25 +
            factual_accuracy * 0.20 +
            uniqueness_score * 0.15 +
            structure_score * 0.15
        )
        
        return ContentQualityMetrics(
            overall_score=overall_score,
            readability_score=readability_score,
            seo_optimization_score=seo_score,
            factual_accuracy_score=factual_accuracy,
            content_uniqueness_score=uniqueness_score,
            keyword_density=keyword_density,
            content_length=content_length,
            structure_score=structure_score
        )
    
    async def _calculate_readability_score(self, content: str) -> float:
        """可読性スコア計算"""
        
        sentences = content.split('。')
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # 日本語可読性の簡易計算
        # 適切な文長: 15-25語
        if 15 <= avg_sentence_length <= 25:
            readability = 90.0
        elif 10 <= avg_sentence_length < 15:
            readability = 80.0
        elif 25 < avg_sentence_length <= 35:
            readability = 75.0
        else:
            readability = 60.0
        
        return readability
    
    async def _calculate_seo_optimization_score(self, content: str, keywords: List[str]) -> float:
        """SEO最適化スコア計算"""
        
        content_lower = content.lower()
        total_words = len(content.split())
        
        seo_scores = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_count = content_lower.count(keyword_lower)
            keyword_density = keyword_count / total_words if total_words > 0 else 0
            
            # 適切なキーワード密度: 1-3%
            if 0.01 <= keyword_density <= 0.03:
                seo_scores.append(90.0)
            elif 0.005 <= keyword_density < 0.01:
                seo_scores.append(75.0)
            elif 0.03 < keyword_density <= 0.05:
                seo_scores.append(70.0)
            else:
                seo_scores.append(50.0)
        
        return statistics.mean(seo_scores) if seo_scores else 0.0
    
    def _calculate_factual_accuracy(self, content: str, expected_elements: List[str]) -> float:
        """事実正確性スコア計算"""
        
        content_lower = content.lower()
        found_elements = []
        
        for element in expected_elements:
            if element.lower() in content_lower:
                found_elements.append(element)
        
        accuracy_rate = len(found_elements) / len(expected_elements) if expected_elements else 1.0
        return accuracy_rate * 100.0
    
    async def _calculate_content_uniqueness(self, content: str) -> float:
        """コンテンツ独自性スコア計算"""
        
        # 簡易実装: 一般的な表現の検出
        common_phrases = [
            "について説明します",
            "ということです",
            "と言われています",
            "することができます"
        ]
        
        content_lower = content.lower()
        common_count = sum(1 for phrase in common_phrases if phrase in content_lower)
        
        # 一般的表現が少ないほど独自性が高い
        uniqueness = max(0, 100 - (common_count * 5))
        return uniqueness
    
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """キーワード密度計算"""
        
        content_lower = content.lower()
        total_words = len(content.split())
        density_map = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_count = content_lower.count(keyword_lower)
            density = (keyword_count / total_words * 100) if total_words > 0 else 0.0
            density_map[keyword] = round(density, 2)
        
        return density_map
    
    def _calculate_structure_score(self, content: str) -> float:
        """構造スコア計算"""
        
        # 見出し構造の評価
        h2_count = content.count('##')
        h3_count = content.count('###')
        
        # 段落数
        paragraph_count = content.count('\n\n')
        
        # 適切な構造の評価
        structure_score = 60.0  # ベーススコア
        
        if h2_count >= 3:  # 適切な見出し数
            structure_score += 15.0
        
        if h3_count >= 2:  # 詳細見出し
            structure_score += 10.0
        
        if paragraph_count >= 5:  # 適切な段落分け
            structure_score += 15.0
        
        return min(100.0, structure_score)
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_seo_optimization_effectiveness(self, content_generator, birth_flower_test_data):
        """
        SEO最適化効果テスト
        
        ビジネスシナリオ: 検索エンジン最適化の効果測定
        成功基準:
        - SEO最適化スコア: 85点以上
        - キーワード密度: 1-3%の範囲
        - メタデータ品質: 90点以上
        """
        
        logger.info("🔍 Testing SEO optimization effectiveness...")
        
        seo_results = []
        
        for month, test_data in birth_flower_test_data.items():
            # SEO最適化されたコンテンツ生成
            result = await content_generator.generate_seo_optimized_content(
                topic=f"{month} birth flowers",
                primary_keyword=test_data["seo_targets"]["primary"],
                secondary_keywords=test_data["seo_targets"]["secondary"],
                content_type="informational_article"
            )
            
            # SEO分析実行
            seo_analysis = await self._analyze_seo_optimization(
                content=result.content,
                title=result.title,
                meta_description=result.meta_description,
                target_keywords=test_data["keywords"]
            )
            
            seo_results.append(seo_analysis)
            
            logger.info(f"   {month.title()} SEO Score: {seo_analysis.title_optimization:.1f}")
        
        # SEO効果の検証
        avg_title_optimization = statistics.mean([r.title_optimization for r in seo_results])
        avg_meta_score = statistics.mean([r.meta_description_score for r in seo_results])
        avg_keyword_distribution = statistics.mean([r.keyword_distribution_score for r in seo_results])
        
        # 成功基準検証
        assert avg_title_optimization >= 85.0, f"Title optimization {avg_title_optimization:.1f} below 85.0"
        assert avg_meta_score >= 90.0, f"Meta description score {avg_meta_score:.1f} below 90.0"
        assert avg_keyword_distribution >= 80.0, f"Keyword distribution {avg_keyword_distribution:.1f} below 80.0"
        
        logger.info(f"🎉 SEO optimization effectiveness verified:")
        logger.info(f"   Title Optimization: {avg_title_optimization:.1f}")
        logger.info(f"   Meta Description: {avg_meta_score:.1f}")
        logger.info(f"   Keyword Distribution: {avg_keyword_distribution:.1f}")
    
    async def _analyze_seo_optimization(self, content: str, title: str, 
                                      meta_description: str, target_keywords: List[str]) -> SEOAnalysisResult:
        """SEO最適化分析"""
        
        # タイトル最適化分析
        title_score = self._analyze_title_optimization(title, target_keywords)
        
        # メタディスクリプション分析
        meta_score = self._analyze_meta_description(meta_description, target_keywords)
        
        # 見出し構造分析
        heading_score = self._analyze_heading_structure(content)
        
        # キーワード分布分析
        keyword_score = self._analyze_keyword_distribution(content, target_keywords)
        
        # 内部リンク機会
        internal_links = self._count_internal_link_opportunities(content)
        
        # コンテンツ深度分析
        depth_score = self._analyze_content_depth(content)
        
        return SEOAnalysisResult(
            title_optimization=title_score,
            meta_description_score=meta_score,
            heading_structure_score=heading_score,
            keyword_distribution_score=keyword_score,
            internal_link_opportunities=internal_links,
            content_depth_score=depth_score
        )
    
    def _analyze_title_optimization(self, title: str, keywords: List[str]) -> float:
        """タイトル最適化分析"""
        
        score = 60.0  # ベーススコア
        title_lower = title.lower()
        
        # 主要キーワードの存在
        for keyword in keywords[:2]:  # 主要な2つのキーワード
            if keyword.lower() in title_lower:
                score += 20.0
        
        # タイトル長の適切性（30-60文字）
        if 30 <= len(title) <= 60:
            score += 10.0
        
        # 数字や年号の存在（クリック率向上）
        if re.search(r'\d{4}|\d+', title):
            score += 10.0
        
        return min(100.0, score)
    
    def _analyze_meta_description(self, meta_description: str, keywords: List[str]) -> float:
        """メタディスクリプション分析"""
        
        if not meta_description:
            return 0.0
        
        score = 70.0  # ベーススコア
        meta_lower = meta_description.lower()
        
        # キーワードの存在
        for keyword in keywords[:3]:  # 主要な3つのキーワード
            if keyword.lower() in meta_lower:
                score += 10.0
        
        # 適切な長さ（120-160文字）
        if 120 <= len(meta_description) <= 160:
            score += 10.0
        
        return min(100.0, score)
    
    def _analyze_heading_structure(self, content: str) -> float:
        """見出し構造分析"""
        
        h1_count = content.count('# ')
        h2_count = content.count('## ')
        h3_count = content.count('### ')
        
        score = 50.0  # ベーススコア
        
        # H1の存在（1つのみが理想）
        if h1_count == 1:
            score += 20.0
        
        # H2の適切な数（3-6個が理想）
        if 3 <= h2_count <= 6:
            score += 20.0
        
        # H3の存在（詳細構造）
        if h3_count >= 2:
            score += 10.0
        
        return score
    
    def _analyze_keyword_distribution(self, content: str, keywords: List[str]) -> float:
        """キーワード分布分析"""
        
        content_lower = content.lower()
        total_words = len(content.split())
        
        distribution_scores = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            positions = [i for i, word in enumerate(content_lower.split()) if keyword_lower in word]
            
            if positions:
                # 均等分布の評価
                distribution_variance = statistics.variance(positions) if len(positions) > 1 else 0
                max_variance = (total_words ** 2) / 4  # 理論的最大分散
                
                distribution_score = max(0, 100 - (distribution_variance / max_variance * 100))
                distribution_scores.append(distribution_score)
        
        return statistics.mean(distribution_scores) if distribution_scores else 0.0
    
    def _count_internal_link_opportunities(self, content: str) -> int:
        """内部リンク機会のカウント"""
        
        # 関連トピックの検出（簡易実装）
        link_opportunities = [
            "誕生花",
            "花言葉", 
            "育て方",
            "花の種類",
            "ガーデニング"
        ]
        
        content_lower = content.lower()
        opportunities = sum(1 for term in link_opportunities if term in content_lower)
        
        return opportunities
    
    def _analyze_content_depth(self, content: str) -> float:
        """コンテンツ深度分析"""
        
        word_count = len(content.split())
        
        # 文章の詳細度評価
        depth_indicators = [
            "について詳しく",
            "具体的には",
            "例えば",
            "一方で",
            "さらに",
            "また",
            "なぜなら"
        ]
        
        content_lower = content.lower()
        depth_count = sum(1 for indicator in depth_indicators if indicator in content_lower)
        
        # 深度スコア計算
        base_score = min(80, word_count / 50)  # 語数による基本スコア
        depth_bonus = min(20, depth_count * 3)  # 深度指標ボーナス
        
        return base_score + depth_bonus
    
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_content_generation_performance_under_load(self, content_generator):
        """
        負荷時コンテンツ生成性能テスト
        
        ビジネスシナリオ: 高負荷時の安定したコンテンツ生成
        成功基準:
        - 同時生成数: 20記事
        - 平均生成時間: 45秒以内
        - 成功率: 90%以上
        """
        
        logger.info("⚡ Testing content generation performance under load...")
        
        # 並行コンテンツ生成タスク
        generation_tasks = []
        
        for i in range(20):
            month = (i % 12) + 1
            task = content_generator.generate_birth_flower_article(
                month=f"month_{month}",
                target_keywords=[f"{month}月", "誕生花", "花言葉"],
                quality_mode="balanced",
                request_id=f"load_test_{i}"
            )
            generation_tasks.append(task)
        
        # 並行実行
        start_time = time.time()
        results = await asyncio.gather(*generation_tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 結果分析
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        success_rate = len(successful_results) / len(results)
        avg_quality = statistics.mean([r.quality_score for r in successful_results]) if successful_results else 0
        
        # 成功基準検証
        assert success_rate >= 0.90, f"Success rate {success_rate:.2%} below 90% threshold"
        assert total_time <= 45.0, f"Total generation time {total_time:.2f}s exceeds 45s limit"
        
        logger.info(f"🎉 Load test completed:")
        logger.info(f"   Success Rate: {success_rate:.2%}")
        logger.info(f"   Average Quality: {avg_quality:.1f}")
        logger.info(f"   Total Time: {total_time:.2f}s")
        logger.info(f"   Failed: {len(failed_results)}")


if __name__ == "__main__":
    # クリティカルパステストのみ実行
    pytest.main([
        __file__,
        "-v", 
        "-m", "critical",
        "--tb=short"
    ])