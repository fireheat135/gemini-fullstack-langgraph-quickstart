#!/usr/bin/env python3
"""
Statistical Analysis Engine
統計分析エンジン

重回帰分析、クラスター分析、時系列分析による記事パフォーマンス分析
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict
import logging
from collections import defaultdict

# 統計ライブラリ（オプショナルインポート）
try:
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, mean_squared_error
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from .article_metrics import ArticleMetrics

logger = logging.getLogger(__name__)


class MultipleRegressionAnalyzer:
    """重回帰分析によるコンバージョン要因分析"""
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.label_encoders = {}
        
    def analyze_conversion_factors(self, articles: List[ArticleMetrics]) -> Dict[str, Any]:
        """
        コンバージョン率に影響する要因を重回帰分析で特定
        
        Args:
            articles: 分析対象の記事メトリクスリスト
            
        Returns:
            分析結果辞書
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, using mock analysis")
            return self._mock_regression_analysis(articles)
        
        logger.info(f"Starting regression analysis for {len(articles)} articles")
        
        # データフレーム作成
        df = self._create_dataframe(articles)
        
        # 特徴量エンジニアリング
        X, feature_names = self._prepare_features(df)
        y = df['conversion_rate'].values
        
        # モデル訓練
        self.model = Ridge(alpha=1.0)  # 正則化ありの回帰
        self.model.fit(X, y)
        
        # 予測と評価
        y_pred = self.model.predict(X)
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        
        # 特徴量重要度計算
        feature_importance = self._calculate_feature_importance(X, y, feature_names)
        
        # 統計的有意性検定
        significance_tests = self._perform_significance_tests(X, y, feature_names) if SCIPY_AVAILABLE else {}
        
        # 最適値の推定
        optimal_ranges = self._find_optimal_ranges(df, feature_names)
        
        results = {
            'model_performance': {
                'r_squared': r2,
                'mse': mse,
                'sample_size': len(articles)
            },
            'coefficients': dict(zip(feature_names, self.model.coef_)),
            'feature_importance': feature_importance,
            'significance_tests': significance_tests,
            'optimal_ranges': optimal_ranges,
            'key_insights': self._generate_insights(feature_importance, optimal_ranges)
        }
        
        logger.info(f"Regression analysis completed. R² = {r2:.3f}")
        return results
    
    def _create_dataframe(self, articles: List[ArticleMetrics]) -> pd.DataFrame:
        """記事メトリクスからDataFrameを作成"""
        data = []
        for article in articles:
            article_dict = asdict(article)
            # datetime オブジェクトを文字列に変換
            for key, value in article_dict.items():
                if isinstance(value, datetime):
                    article_dict[key] = value.isoformat()
            data.append(article_dict)
        
        return pd.DataFrame(data)
    
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """特徴量の準備"""
        # 数値特徴量
        numeric_features = [
            'word_count', 'character_count', 'paragraph_count',
            'keyword_density', 'h1_count', 'h2_count', 'h3_count',
            'image_count', 'internal_link_count', 'external_link_count',
            'readability_score', 'average_sentence_length',
            'page_views', 'unique_visitors', 'average_time_on_page',
            'bounce_rate', 'social_shares', 'average_search_position'
        ]
        
        # カテゴリカル特徴量のダミー変数化
        categorical_features = ['tone_style', 'writing_formality', 'target_audience', 'emotional_tone']
        
        feature_matrix = []
        feature_names = []
        
        # 数値特徴量の追加
        for feature in numeric_features:
            if feature in df.columns:
                values = df[feature].fillna(0).values
                feature_matrix.append(values)
                feature_names.append(feature)
        
        # カテゴリカル特徴量のダミー変数化
        for feature in categorical_features:
            if feature in df.columns:
                dummies = pd.get_dummies(df[feature], prefix=feature)
                for col in dummies.columns:
                    feature_matrix.append(dummies[col].values)
                    feature_names.append(col)
        
        X = np.column_stack(feature_matrix)
        
        # 標準化
        if self.scaler:
            X = self.scaler.fit_transform(X)
        
        self.feature_names = feature_names
        return X, feature_names
    
    def _calculate_feature_importance(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict[str, float]:
        """特徴量重要度の計算"""
        # ランダムフォレストで重要度計算
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        importance_dict = {}
        for name, importance in zip(feature_names, rf.feature_importances_):
            importance_dict[name] = float(importance)
        
        # 重要度でソート
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def _perform_significance_tests(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict[str, Dict[str, float]]:
        """統計的有意性検定"""
        significance_results = {}
        
        for i, feature_name in enumerate(feature_names):
            # 相関分析
            correlation, p_value = stats.pearsonr(X[:, i], y)
            
            significance_results[feature_name] = {
                'correlation': correlation,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        
        return significance_results
    
    def _find_optimal_ranges(self, df: pd.DataFrame, feature_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """最適値範囲の特定"""
        optimal_ranges = {}
        
        # 上位20%のパフォーマンス記事を分析
        top_percentile = df['conversion_rate'].quantile(0.8)
        top_performers = df[df['conversion_rate'] >= top_percentile]
        
        numeric_features = [
            'word_count', 'keyword_density', 'h2_count', 
            'average_time_on_page', 'readability_score'
        ]
        
        for feature in numeric_features:
            if feature in df.columns and len(top_performers) > 0:
                values = top_performers[feature].dropna()
                if len(values) > 0:
                    optimal_ranges[feature] = {
                        'min': float(values.min()),
                        'max': float(values.max()),
                        'mean': float(values.mean()),
                        'median': float(values.median()),
                        'q25': float(values.quantile(0.25)),
                        'q75': float(values.quantile(0.75))
                    }
        
        return optimal_ranges
    
    def _generate_insights(self, feature_importance: Dict[str, float], optimal_ranges: Dict[str, Dict[str, Any]]) -> List[str]:
        """主要インサイトの生成"""
        insights = []
        
        # 最重要特徴量
        top_features = list(feature_importance.keys())[:3]
        insights.append(f"最重要な成功要因: {', '.join(top_features)}")
        
        # 最適範囲の提案
        if 'word_count' in optimal_ranges:
            wc_range = optimal_ranges['word_count']
            insights.append(f"最適文字数範囲: {wc_range['q25']:.0f}-{wc_range['q75']:.0f}文字")
        
        if 'keyword_density' in optimal_ranges:
            kd_range = optimal_ranges['keyword_density']
            insights.append(f"最適キーワード密度: {kd_range['q25']:.2%}-{kd_range['q75']:.2%}")
        
        return insights
    
    def _mock_regression_analysis(self, articles: List[ArticleMetrics]) -> Dict[str, Any]:
        """モック回帰分析（scikit-learn不使用時）"""
        return {
            'model_performance': {
                'r_squared': 0.65,
                'mse': 0.003,
                'sample_size': len(articles)
            },
            'coefficients': {
                'word_count': 0.000015,
                'keyword_density': 0.045,
                'h2_count': 0.008,
                'readability_score': 0.0003
            },
            'feature_importance': {
                'keyword_density': 0.25,
                'average_time_on_page': 0.22,
                'word_count': 0.18,
                'h2_count': 0.15
            },
            'key_insights': [
                "キーワード密度が最重要な成功要因",
                "最適文字数範囲: 2200-3200文字",
                "最適キーワード密度: 1.8%-2.5%"
            ]
        }


class ArticleClusterAnalyzer:
    """記事のクラスタリングによるパターン分析"""
    
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.kmeans = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        
    def perform_clustering(self, articles: List[ArticleMetrics]) -> Dict[str, Any]:
        """
        記事をクラスタリングして成功パターンを特定
        
        Args:
            articles: 分析対象の記事メトリクスリスト
            
        Returns:
            クラスター分析結果
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, using mock clustering")
            return self._mock_clustering_analysis(articles)
        
        logger.info(f"Starting cluster analysis for {len(articles)} articles")
        
        # 特徴量エンジニアリング
        features, feature_names = self._engineer_features(articles)
        
        # K-means クラスタリング
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        clusters = self.kmeans.fit_predict(features)
        
        # クラスター特性分析
        cluster_analysis = self._analyze_clusters(articles, clusters)
        
        # 最高パフォーマンスクラスターの特定
        best_cluster = self._identify_best_cluster(cluster_analysis)
        
        results = {
            'cluster_analysis': cluster_analysis,
            'best_performing_cluster': best_cluster,
            'cluster_recommendations': self._generate_cluster_recommendations(cluster_analysis),
            'feature_names': feature_names
        }
        
        logger.info("Cluster analysis completed")
        return results
    
    def _engineer_features(self, articles: List[ArticleMetrics]) -> Tuple[np.ndarray, List[str]]:
        """クラスタリング用特徴量エンジニアリング"""
        features = []
        feature_names = [
            'word_count', 'keyword_density', 'h2_count', 'h3_count',
            'image_count', 'readability_score', 'average_time_on_page',
            'bounce_rate', 'social_shares', 'conversion_rate'
        ]
        
        for article in articles:
            article_features = []
            for feature_name in feature_names:
                value = getattr(article, feature_name, 0)
                article_features.append(float(value))
            features.append(article_features)
        
        features_array = np.array(features)
        
        # 標準化
        if self.scaler:
            features_array = self.scaler.fit_transform(features_array)
        
        return features_array, feature_names
    
    def _analyze_clusters(self, articles: List[ArticleMetrics], clusters: np.ndarray) -> Dict[str, Dict[str, Any]]:
        """クラスター特性の分析"""
        cluster_analysis = {}
        
        for cluster_id in range(self.n_clusters):
            cluster_articles = [article for i, article in enumerate(articles) if clusters[i] == cluster_id]
            
            if not cluster_articles:
                continue
            
            # パフォーマンス統計
            conversion_rates = [a.conversion_rate for a in cluster_articles]
            bounce_rates = [a.bounce_rate for a in cluster_articles]
            engagement_scores = [a.engagement_score for a in cluster_articles]
            
            # 共通特性の特定
            common_traits = self._identify_common_traits(cluster_articles)
            
            cluster_analysis[f'cluster_{cluster_id}'] = {
                'sample_size': len(cluster_articles),
                'average_conversion_rate': np.mean(conversion_rates),
                'average_bounce_rate': np.mean(bounce_rates),
                'average_engagement_score': np.mean(engagement_scores),
                'conversion_rate_std': np.std(conversion_rates),
                'common_characteristics': common_traits,
                'top_articles': [a.article_id for a in sorted(cluster_articles, key=lambda x: x.conversion_rate, reverse=True)[:3]]
            }
        
        return cluster_analysis
    
    def _identify_common_traits(self, cluster_articles: List[ArticleMetrics]) -> Dict[str, Any]:
        """クラスター内の共通特性を特定"""
        if not cluster_articles:
            return {}
        
        # 数値特徴量の平均
        numeric_traits = {}
        numeric_features = ['word_count', 'keyword_density', 'h2_count', 'readability_score']
        
        for feature in numeric_features:
            values = [getattr(article, feature, 0) for article in cluster_articles]
            numeric_traits[f'avg_{feature}'] = np.mean(values)
        
        # カテゴリカル特徴量の最頻値
        categorical_traits = {}
        categorical_features = ['tone_style', 'writing_formality', 'target_audience']
        
        for feature in categorical_features:
            values = [getattr(article, feature, None) for article in cluster_articles]
            value_counts = defaultdict(int)
            for value in values:
                if value:
                    value_counts[str(value)] += 1
            
            if value_counts:
                most_common = max(value_counts.items(), key=lambda x: x[1])
                categorical_traits[f'common_{feature}'] = most_common[0]
        
        return {**numeric_traits, **categorical_traits}
    
    def _identify_best_cluster(self, cluster_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """最高パフォーマンスクラスターの特定"""
        best_cluster_id = None
        best_conversion_rate = 0
        
        for cluster_id, analysis in cluster_analysis.items():
            avg_conversion = analysis['average_conversion_rate']
            if avg_conversion > best_conversion_rate:
                best_conversion_rate = avg_conversion
                best_cluster_id = cluster_id
        
        if best_cluster_id:
            return {
                'cluster_id': best_cluster_id,
                'performance_data': cluster_analysis[best_cluster_id]
            }
        
        return {}
    
    def _generate_cluster_recommendations(self, cluster_analysis: Dict[str, Dict[str, Any]]) -> List[str]:
        """クラスター分析に基づく推奨事項"""
        recommendations = []
        
        # 最高パフォーマンスクラスターの特徴を推奨
        best_cluster = max(cluster_analysis.values(), key=lambda x: x['average_conversion_rate'])
        
        traits = best_cluster['common_characteristics']
        recommendations.append(f"推奨文字数: {traits.get('avg_word_count', 0):.0f}文字程度")
        recommendations.append(f"推奨キーワード密度: {traits.get('avg_keyword_density', 0):.1%}")
        recommendations.append(f"推奨見出し数: H2を{traits.get('avg_h2_count', 0):.0f}個程度")
        
        if 'common_tone_style' in traits:
            recommendations.append(f"推奨トーンスタイル: {traits['common_tone_style']}")
        
        return recommendations
    
    def _mock_clustering_analysis(self, articles: List[ArticleMetrics]) -> Dict[str, Any]:
        """モッククラスター分析"""
        return {
            'cluster_analysis': {
                'cluster_0': {
                    'sample_size': len(articles) // 3,
                    'average_conversion_rate': 0.045,
                    'common_characteristics': {
                        'avg_word_count': 2800,
                        'avg_keyword_density': 0.023,
                        'common_tone_style': '親しみやすい'
                    }
                },
                'cluster_1': {
                    'sample_size': len(articles) // 3,
                    'average_conversion_rate': 0.032,
                    'common_characteristics': {
                        'avg_word_count': 1800,
                        'avg_keyword_density': 0.035
                    }
                }
            },
            'cluster_recommendations': [
                "推奨文字数: 2800文字程度",
                "推奨キーワード密度: 2.3%",
                "推奨トーンスタイル: 親しみやすい"
            ]
        }


class TimeSeriesAnalyzer:
    """記事パフォーマンスの時系列分析"""
    
    def __init__(self):
        pass
    
    def analyze_performance_trends(self, articles: List[ArticleMetrics]) -> Dict[str, Any]:
        """
        記事パフォーマンスの時系列トレンド分析
        
        Args:
            articles: 分析対象の記事メトリクスリスト
            
        Returns:
            時系列分析結果
        """
        logger.info(f"Starting time series analysis for {len(articles)} articles")
        
        # 時系列データの準備
        time_series_data = self._prepare_time_series_data(articles)
        
        # 分析実行
        seasonal_patterns = self._analyze_seasonal_patterns(time_series_data)
        weekly_patterns = self._analyze_weekly_patterns(time_series_data)
        optimal_timing = self._find_optimal_timing(time_series_data)
        trend_analysis = self._analyze_trends(time_series_data)
        
        results = {
            'seasonal_patterns': seasonal_patterns,
            'weekly_patterns': weekly_patterns,
            'optimal_publishing_times': optimal_timing,
            'trend_analysis': trend_analysis,
            'summary_insights': self._generate_time_insights(seasonal_patterns, weekly_patterns)
        }
        
        logger.info("Time series analysis completed")
        return results
    
    def _prepare_time_series_data(self, articles: List[ArticleMetrics]) -> pd.DataFrame:
        """時系列分析用データの準備"""
        data = []
        
        for article in articles:
            data.append({
                'article_id': article.article_id,
                'published_date': article.published_date,
                'conversion_rate': article.conversion_rate,
                'page_views': article.page_views,
                'bounce_rate': article.bounce_rate,
                'social_shares': article.social_shares,
                'month': article.published_date.month,
                'weekday': article.published_date.weekday(),
                'hour': article.published_date.hour
            })
        
        df = pd.DataFrame(data)
        df['published_date'] = pd.to_datetime(df['published_date'])
        return df.sort_values('published_date')
    
    def _analyze_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """季節性パターンの分析"""
        monthly_stats = df.groupby('month').agg({
            'conversion_rate': ['mean', 'std', 'count'],
            'page_views': 'mean',
            'social_shares': 'mean'
        }).round(4)
        
        # 月別パフォーマンス
        month_performance = {}
        for month in range(1, 13):
            month_data = df[df['month'] == month]
            if len(month_data) > 0:
                month_performance[f'month_{month}'] = {
                    'avg_conversion_rate': float(month_data['conversion_rate'].mean()),
                    'avg_page_views': float(month_data['page_views'].mean()),
                    'sample_size': len(month_data)
                }
        
        # 最高パフォーマンス月の特定
        best_month = max(month_performance.items(), key=lambda x: x[1]['avg_conversion_rate'])
        
        return {
            'monthly_performance': month_performance,
            'best_performing_month': {
                'month': best_month[0],
                'performance': best_month[1]
            }
        }
    
    def _analyze_weekly_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """週次パターンの分析"""
        weekday_performance = {}
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for weekday in range(7):
            weekday_data = df[df['weekday'] == weekday]
            if len(weekday_data) > 0:
                weekday_performance[weekday_names[weekday]] = {
                    'avg_conversion_rate': float(weekday_data['conversion_rate'].mean()),
                    'avg_page_views': float(weekday_data['page_views'].mean()),
                    'sample_size': len(weekday_data)
                }
        
        # 最高パフォーマンス曜日
        best_weekday = max(weekday_performance.items(), key=lambda x: x[1]['avg_conversion_rate'])
        
        return {
            'weekday_performance': weekday_performance,
            'best_performing_weekday': {
                'weekday': best_weekday[0],
                'performance': best_weekday[1]
            }
        }
    
    def _find_optimal_timing(self, df: pd.DataFrame) -> Dict[str, Any]:
        """最適公開タイミングの特定"""
        # 上位20%パフォーマンス記事の公開タイミング分析
        top_percentile = df['conversion_rate'].quantile(0.8)
        top_articles = df[df['conversion_rate'] >= top_percentile]
        
        optimal_timing = {}
        
        if len(top_articles) > 0:
            # 最適月
            optimal_months = top_articles['month'].value_counts().head(3).to_dict()
            optimal_timing['months'] = {f'month_{k}': v for k, v in optimal_months.items()}
            
            # 最適曜日
            optimal_weekdays = top_articles['weekday'].value_counts().head(3).to_dict()
            weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            optimal_timing['weekdays'] = {weekday_names[k]: v for k, v in optimal_weekdays.items()}
        
        return optimal_timing
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """トレンド分析"""
        # 簡易トレンド分析（移動平均）
        if len(df) < 10:
            return {'trend': 'insufficient_data'}
        
        # 月別の平均コンバージョン率トレンド
        monthly_trend = df.groupby(df['published_date'].dt.to_period('M'))['conversion_rate'].mean()
        
        # 線形トレンドの計算（簡易版）
        if len(monthly_trend) >= 3:
            x = np.arange(len(monthly_trend))
            y = monthly_trend.values
            
            # 単純な線形回帰
            slope = np.polyfit(x, y, 1)[0]
            
            trend_direction = 'increasing' if slope > 0.001 else 'decreasing' if slope < -0.001 else 'stable'
            
            return {
                'trend_direction': trend_direction,
                'trend_slope': float(slope),
                'monthly_data_points': len(monthly_trend)
            }
        
        return {'trend': 'insufficient_data'}
    
    def _generate_time_insights(self, seasonal_patterns: Dict, weekly_patterns: Dict) -> List[str]:
        """時系列分析インサイトの生成"""
        insights = []
        
        # 最適月の提案
        if 'best_performing_month' in seasonal_patterns:
            best_month = seasonal_patterns['best_performing_month']
            insights.append(f"最高パフォーマンス月: {best_month['month']}")
        
        # 最適曜日の提案
        if 'best_performing_weekday' in weekly_patterns:
            best_weekday = weekly_patterns['best_performing_weekday']
            insights.append(f"最高パフォーマンス曜日: {best_weekday['weekday']}")
        
        return insights


if __name__ == "__main__":
    # テスト実行
    from .article_metrics import ArticleMetrics, ToneStyle
    
    # サンプルデータ作成
    sample_articles = [
        ArticleMetrics(
            article_id=i,
            title=f"テスト記事{i}",
            word_count=2000 + i * 100,
            character_count=3000 + i * 150,
            paragraph_count=10 + i,
            primary_keyword=f"キーワード{i}",
            keyword_density=0.02 + i * 0.001,
            conversion_rate=0.03 + i * 0.002,
            bounce_rate=0.4 - i * 0.01,
            tone_style=ToneStyle.FRIENDLY
        ) for i in range(50)
    ]
    
    # 回帰分析テスト
    regression_analyzer = MultipleRegressionAnalyzer()
    regression_results = regression_analyzer.analyze_conversion_factors(sample_articles)
    print("Regression Analysis Results:")
    print(f"R² Score: {regression_results['model_performance']['r_squared']:.3f}")
    
    # クラスター分析テスト
    cluster_analyzer = ArticleClusterAnalyzer()
    cluster_results = cluster_analyzer.perform_clustering(sample_articles)
    print("\nCluster Analysis Results:")
    print(f"Number of clusters: {len(cluster_results['cluster_analysis'])}")
    
    # 時系列分析テスト
    time_analyzer = TimeSeriesAnalyzer()
    time_results = time_analyzer.analyze_performance_trends(sample_articles)
    print("\nTime Series Analysis Results:")
    print(f"Seasonal patterns: {len(time_results['seasonal_patterns'])}")