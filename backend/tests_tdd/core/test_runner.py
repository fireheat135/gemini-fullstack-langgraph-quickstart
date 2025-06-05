#!/usr/bin/env python3
"""
TDD テストランナー

自己回帰ループによるテスト実行とメトリクス収集
"""

import os
import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .coverage_monitor import CoverageMonitor
from .quality_evaluator import QualityEvaluator
from .convergence_checker import ConvergenceChecker


@dataclass
class TestResult:
    """テスト結果データクラス"""
    test_name: str
    passed: bool
    execution_time: float
    coverage: float
    quality_score: float
    issues: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any] = None


@dataclass
class TDDLoopResult:
    """TDDループ結果データクラス"""
    iterations: int
    converged: bool
    final_metrics: Dict[str, float]
    improvement_trend: Dict[str, Any]
    recommendations: List[str]
    test_results: List[TestResult]
    execution_time: float


class TDDTestRunner:
    """
    テスト駆動開発のメインランナー
    
    自己回帰ループでテストを実行し、品質指標が閾値に達するまで改善を継続
    """
    
    def __init__(
        self,
        coverage_threshold: float = 0.8,
        quality_threshold: float = 0.9,
        max_iterations: int = 5,
        config_path: Optional[str] = None
    ):
        self.coverage_threshold = coverage_threshold
        self.quality_threshold = quality_threshold
        self.max_iterations = max_iterations
        
        # コンポーネント初期化
        self.coverage_monitor = CoverageMonitor(threshold=coverage_threshold)
        self.quality_evaluator = QualityEvaluator()
        self.convergence_checker = ConvergenceChecker(
            thresholds={
                'coverage': coverage_threshold,
                'quality_score': quality_threshold,
                'success_rate': 0.8
            }
        )
        
        # 実行履歴
        self.loop_history = []
        self.current_iteration = 0
        
    async def run_self_recursive_loop(self, test_modules: List[str]) -> TDDLoopResult:
        """
        自己回帰テストループの実行
        
        Args:
            test_modules: 実行するテストモジュールのリスト
            
        Returns:
            TDDLoopResult: ループ実行結果
        """
        print("🔄 TDD自己回帰ループ開始")
        print("="*60)
        
        start_time = time.time()
        
        for iteration in range(self.max_iterations):
            self.current_iteration = iteration + 1
            print(f"\n📍 反復 {self.current_iteration}/{self.max_iterations}")
            
            # テストスイート実行
            iteration_results = await self._run_test_iteration(test_modules)
            self.loop_history.append(iteration_results)
            
            # メトリクス計算
            metrics = self._calculate_iteration_metrics(iteration_results)
            
            # 収束判定
            convergence = self.convergence_checker.check_convergence(metrics)
            
            self._print_iteration_summary(metrics, convergence)
            
            if convergence.converged:
                print(f"✅ 収束完了！({iteration + 1}回目で基準達成)")
                break
            else:
                print(f"🔄 改善が必要: {convergence.reason}")
                # 自動改善適用
                await self._apply_improvements(convergence.suggestions)
        
        total_time = time.time() - start_time
        
        # 最終レポート生成
        final_result = self._generate_final_result(total_time)
        
        print(f"\n🎉 TDDループ完了 (実行時間: {total_time:.2f}s)")
        return final_result
    
    async def _run_test_iteration(self, test_modules: List[str]) -> List[TestResult]:
        """単一反復のテスト実行"""
        results = []
        
        for module in test_modules:
            try:
                result = await self._execute_test_module(module)
                results.append(result)
                status = "✅" if result.passed else "❌"
                print(f"   {status} {result.test_name}: Q={result.quality_score:.2f}")
            except Exception as e:
                error_result = TestResult(
                    test_name=module,
                    passed=False,
                    execution_time=0.0,
                    coverage=0.0,
                    quality_score=0.0,
                    issues=[str(e)],
                    suggestions=["エラーハンドリングを確認してください"]
                )
                results.append(error_result)
                print(f"   ❌ {module}: Exception - {e}")
        
        return results
    
    async def _execute_test_module(self, module: str) -> TestResult:
        """個別テストモジュールの実行"""
        start_time = time.time()
        
        # ここで実際のテスト実行ロジックを実装
        # 例: pytest, unittest, カスタムテストランナーなど
        
        # モックアップ実装（実際の実装では置き換え）
        await asyncio.sleep(0.1)  # テスト実行シミュレーション
        
        execution_time = time.time() - start_time
        
        # カバレッジ測定
        coverage = self.coverage_monitor.measure_coverage(module)
        
        # 品質評価
        quality_score = self.quality_evaluator.evaluate_module(module)
        
        return TestResult(
            test_name=module,
            passed=quality_score > 0.7,
            execution_time=execution_time,
            coverage=coverage,
            quality_score=quality_score,
            issues=[],
            suggestions=[]
        )
    
    def _calculate_iteration_metrics(self, results: List[TestResult]) -> Dict[str, float]:
        """反復メトリクスの計算"""
        if not results:
            return {'coverage': 0.0, 'quality_score': 0.0, 'success_rate': 0.0}
        
        total_coverage = sum(r.coverage for r in results) / len(results)
        total_quality = sum(r.quality_score for r in results) / len(results)
        success_rate = sum(1 for r in results if r.passed) / len(results)
        
        return {
            'coverage': total_coverage,
            'quality_score': total_quality,
            'success_rate': success_rate
        }
    
    def _print_iteration_summary(self, metrics: Dict[str, float], convergence):
        """反復結果のサマリー表示"""
        print(f"📊 メトリクス:")
        print(f"   カバレッジ: {metrics['coverage']:.1%}")
        print(f"   品質スコア: {metrics['quality_score']:.1%}")
        print(f"   成功率: {metrics['success_rate']:.1%}")
        
        if not convergence.converged:
            print(f"🔍 改善点:")
            for suggestion in convergence.suggestions:
                print(f"   • {suggestion}")
    
    async def _apply_improvements(self, suggestions: List[str]):
        """自動改善の適用"""
        print(f"🔧 改善を適用中:")
        for suggestion in suggestions:
            print(f"   • {suggestion}")
        
        # 実際の改善ロジックをここに実装
        await asyncio.sleep(0.5)  # 改善処理シミュレーション
    
    def _generate_final_result(self, execution_time: float) -> TDDLoopResult:
        """最終結果の生成"""
        final_iteration = self.loop_history[-1] if self.loop_history else []
        final_metrics = self._calculate_iteration_metrics(final_iteration)
        
        return TDDLoopResult(
            iterations=len(self.loop_history),
            converged=final_metrics.get('quality_score', 0) >= self.quality_threshold,
            final_metrics=final_metrics,
            improvement_trend=self._analyze_improvement_trend(),
            recommendations=self._generate_recommendations(final_iteration),
            test_results=final_iteration,
            execution_time=execution_time
        )
    
    def _analyze_improvement_trend(self) -> Dict[str, Any]:
        """改善傾向の分析"""
        if len(self.loop_history) < 2:
            return {'trend': 'insufficient_data'}
        
        metrics_over_time = [
            self._calculate_iteration_metrics(results) 
            for results in self.loop_history
        ]
        
        coverage_trend = [m['coverage'] for m in metrics_over_time]
        quality_trend = [m['quality_score'] for m in metrics_over_time]
        
        return {
            'coverage_improvement': coverage_trend[-1] - coverage_trend[0],
            'quality_improvement': quality_trend[-1] - quality_trend[0],
            'convergence_speed': len(self.loop_history),
            'stability': self._calculate_stability(metrics_over_time)
        }
    
    def _calculate_stability(self, metrics_over_time: List[Dict[str, float]]) -> float:
        """安定性の計算"""
        if len(metrics_over_time) < 3:
            return 0.0
        
        recent_metrics = metrics_over_time[-3:]
        variances = []
        
        for key in ['coverage', 'quality_score', 'success_rate']:
            values = [m[key] for m in recent_metrics]
            mean = sum(values) / len(values)
            variance = sum((v - mean)**2 for v in values) / len(values)
            variances.append(variance)
        
        return 1.0 - sum(variances) / len(variances)
    
    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """推奨事項の生成"""
        recommendations = []
        
        if not results:
            recommendations.append("基本テストケースを実装してください")
            return recommendations
        
        failed_tests = [r for r in results if not r.passed]
        if failed_tests:
            recommendations.append(f"{len(failed_tests)}個の失敗テストを優先的に修正")
        
        low_coverage_tests = [r for r in results if r.coverage < self.coverage_threshold]
        if low_coverage_tests:
            recommendations.append("カバレッジが低いテストケースを強化")
        
        low_quality_tests = [r for r in results if r.quality_score < self.quality_threshold]
        if low_quality_tests:
            recommendations.append("品質スコアが低いテストの改善")
        
        if all(r.passed for r in results):
            recommendations.append("全テスト成功！追加のエッジケースを検討")
        
        return recommendations