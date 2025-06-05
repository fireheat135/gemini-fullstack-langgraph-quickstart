"""
Convergence Checker
収束判定システム
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ConvergenceResult:
    """収束判定結果"""
    converged: bool
    iterations: int
    reason: Optional[str] = None
    suggestions: List[str] = None
    final_metrics: Optional[Dict[str, float]] = None
    manual_intervention_required: bool = False
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


@dataclass
class Metrics:
    """メトリクス情報"""
    coverage: float
    quality_score: float
    success_rate: float
    execution_time: float = 0.0
    
    def get(self, key: str, default=None):
        """辞書風のアクセスメソッド"""
        return getattr(self, key, default)


class ConvergenceChecker:
    """収束判定チェッカー"""
    
    def __init__(self, thresholds: Dict[str, float]):
        self.thresholds = thresholds
        self.history = []
        self.max_iterations = 10
        self.stagnation_threshold = 3  # 改善が停滞と判断する連続回数
        
    def check_convergence(self, metrics: Dict[str, float]) -> ConvergenceResult:
        """収束条件を満たしているか判定"""
        
        # メトリクス型に変換
        if isinstance(metrics, dict):
            metrics_obj = Metrics(
                coverage=metrics.get('coverage', 0.0),
                quality_score=metrics.get('quality_score', 0.0),
                success_rate=metrics.get('success_rate', 0.0),
                execution_time=metrics.get('execution_time', 0.0)
            )
        else:
            metrics_obj = metrics
            
        self.history.append(metrics_obj)
        
        # 全閾値を満たしているか
        all_passed = self._check_all_thresholds(metrics_obj)
        
        if all_passed:
            return ConvergenceResult(
                converged=True,
                iterations=len(self.history),
                final_metrics=self._metrics_to_dict(metrics_obj),
                reason="全ての品質基準を満たしました"
            )
        
        # 改善が停滞していないか
        if len(self.history) >= self.stagnation_threshold:
            if self._is_stagnant():
                return ConvergenceResult(
                    converged=False,
                    iterations=len(self.history),
                    reason="改善が停滞しています",
                    suggestions=self._generate_breakthrough_suggestions()
                )
        
        # 最大反復回数に達したか
        if len(self.history) >= self.max_iterations:
            return ConvergenceResult(
                converged=False,
                iterations=len(self.history),
                reason="最大反復回数に達しました",
                manual_intervention_required=True,
                suggestions=["手動での介入が必要です"]
            )
        
        # 次のアクションを決定
        next_actions = self._determine_next_actions(metrics_obj)
        
        return ConvergenceResult(
            converged=False,
            iterations=len(self.history),
            reason="改善継続中",
            suggestions=next_actions
        )
    
    def _check_all_thresholds(self, metrics: Metrics) -> bool:
        """全ての閾値をクリアしているかチェック"""
        checks = []
        
        if 'coverage' in self.thresholds:
            checks.append(metrics.coverage >= self.thresholds['coverage'])
            
        if 'quality_score' in self.thresholds:
            checks.append(metrics.quality_score >= self.thresholds['quality_score'])
            
        if 'success_rate' in self.thresholds:
            checks.append(metrics.success_rate >= self.thresholds['success_rate'])
        
        return all(checks)
    
    def _is_stagnant(self) -> bool:
        """改善が停滞しているかチェック"""
        if len(self.history) < self.stagnation_threshold:
            return False
            
        # 直近の改善率をチェック
        recent_metrics = self.history[-self.stagnation_threshold:]
        
        # 各メトリクスの改善を確認
        coverage_improvement = self._calculate_improvement(
            [m.coverage for m in recent_metrics]
        )
        quality_improvement = self._calculate_improvement(
            [m.quality_score for m in recent_metrics]
        )
        success_improvement = self._calculate_improvement(
            [m.success_rate for m in recent_metrics]
        )
        
        # 改善が微小な場合は停滞と判断
        stagnation_threshold = 0.01  # 1%以下の改善は停滞
        
        return (
            abs(coverage_improvement) < stagnation_threshold and
            abs(quality_improvement) < stagnation_threshold and
            abs(success_improvement) < stagnation_threshold
        )
    
    def _calculate_improvement(self, values: List[float]) -> float:
        """値の改善率を計算"""
        if len(values) < 2:
            return 0.0
        
        return values[-1] - values[0]
    
    def _determine_next_actions(self, metrics: Metrics) -> List[str]:
        """次のアクションを決定"""
        actions = []
        
        # カバレッジ不足の場合
        if 'coverage' in self.thresholds and metrics.coverage < self.thresholds['coverage']:
            deficit = self.thresholds['coverage'] - metrics.coverage
            if deficit > 0.2:
                actions.append("追加のテストケースを大幅に増やしてください")
            else:
                actions.append("エッジケースのテストを追加してください")
        
        # 品質スコア不足の場合
        if 'quality_score' in self.thresholds and metrics.quality_score < self.thresholds['quality_score']:
            deficit = self.thresholds['quality_score'] - metrics.quality_score
            if deficit > 0.2:
                actions.append("テストの品質を根本的に見直してください")
            else:
                actions.append("アサーションの精度を向上させてください")
        
        # 成功率不足の場合
        if 'success_rate' in self.thresholds and metrics.success_rate < self.thresholds['success_rate']:
            actions.append("失敗しているテストを修正してください")
        
        # 一般的なアドバイス
        if not actions:
            actions.append("既存のテストを強化してください")
        
        return actions
    
    def _generate_breakthrough_suggestions(self) -> List[str]:
        """停滞突破のための提案を生成"""
        return [
            "テスト戦略を根本的に見直してください",
            "新しいテストアプローチを試してください",
            "プロパティベーステストを導入してください",
            "AI支援テスト生成を活用してください",
            "テストデータ生成戦略を変更してください"
        ]
    
    def _metrics_to_dict(self, metrics: Metrics) -> Dict[str, float]:
        """Metricsオブジェクトを辞書に変換"""
        return {
            'coverage': metrics.coverage,
            'quality_score': metrics.quality_score,
            'success_rate': metrics.success_rate,
            'execution_time': metrics.execution_time
        }
    
    def reset(self):
        """履歴をリセット"""
        self.history = []
    
    def get_improvement_trend(self) -> Dict[str, Any]:
        """改善傾向を分析"""
        if len(self.history) < 2:
            return {'status': 'insufficient_data'}
        
        first = self.history[0]
        last = self.history[-1]
        
        return {
            'coverage_change': last.coverage - first.coverage,
            'quality_change': last.quality_score - first.quality_score,
            'success_rate_change': last.success_rate - first.success_rate,
            'total_iterations': len(self.history),
            'trend': 'improving' if last.quality_score > first.quality_score else 'declining'
        }