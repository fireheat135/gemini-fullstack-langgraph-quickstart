"""
Analytics module for data-driven article analysis
データドリブン記事分析モジュール
"""

from .article_metrics import ArticleMetrics, ArticleMetricsManager

# オプショナルインポート
try:
    from .statistical_analyzer import (
        MultipleRegressionAnalyzer,
        ArticleClusterAnalyzer, 
        TimeSeriesAnalyzer
    )
    STATISTICAL_ANALYZER_AVAILABLE = True
except ImportError:
    STATISTICAL_ANALYZER_AVAILABLE = False
    MultipleRegressionAnalyzer = None
    ArticleClusterAnalyzer = None
    TimeSeriesAnalyzer = None

# その他の未実装モジュール（将来実装予定）
try:
    from .tag_extractor import AutoTagExtractor, CustomTagManager
except ImportError:
    AutoTagExtractor = None
    CustomTagManager = None

try:
    from .performance_predictor import PerformancePredictor
except ImportError:
    PerformancePredictor = None

try:
    from .best_practice_extractor import BestPracticeExtractor
except ImportError:
    BestPracticeExtractor = None

try:
    from .report_generator import StatisticalReportGenerator
except ImportError:
    StatisticalReportGenerator = None

__all__ = [
    'ArticleMetrics',
    'ArticleMetricsManager',
    'MultipleRegressionAnalyzer',
    'ArticleClusterAnalyzer',
    'TimeSeriesAnalyzer',
    'AutoTagExtractor',
    'CustomTagManager',
    'PerformancePredictor',
    'BestPracticeExtractor',
    'StatisticalReportGenerator',
    'STATISTICAL_ANALYZER_AVAILABLE'
]