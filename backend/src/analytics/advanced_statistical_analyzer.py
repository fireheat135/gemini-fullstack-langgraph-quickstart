#!/usr/bin/env python3
"""
高度な統計分析エンジン
因果推論・重回帰分析・クラスター分析による記事パフォーマンスの科学的分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 統計・機械学習ライブラリ
try:
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import silhouette_score, r2_score
    from sklearn.model_selection import train_test_split
    from scipy import stats
    from scipy.stats import ttest_ind, chi2_contingency
    import statsmodels.api as sm
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.stats.outliers_influence import variance_inflation_factor
except ImportError:
    print("警告: 統計分析ライブラリが不足しています。pip install scikit-learn scipy statsmodels を実行してください。")


@dataclass
class ArticlePerformanceData:
    """記事パフォーマンスデータ"""
    article_id: str
    title: str
    publish_date: datetime
    word_count: int
    keyword_density: float
    seo_score: float
    tone_manner: str
    author: str
    category: str
    
    # パフォーマンス指標
    pv_daily: List[int]
    unique_users: List[int] 
    avg_time_on_page: List[float]
    bounce_rate: List[float]
    social_shares: List[int]
    conversions: List[int]
    
    # SEO指標
    search_impressions: List[int]
    search_clicks: List[int]
    avg_position: List[float]
    
    # タグ・メタデータ
    tags: List[str]
    promotion_activities: List[str]
    external_events: List[str]


@dataclass 
class CausalInferenceResult:
    """因果推論結果"""
    method: str
    treatment_effect: float
    confidence_interval: Tuple[float, float]
    p_value: float
    statistical_significance: bool
    effect_size: str
    interpretation: str
    recommendations: List[str]


class AdvancedStatisticalAnalyzer:
    """高度統計分析エンジン"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    # ============================================================
    # データ前処理・準備
    # ============================================================
    
    def prepare_analysis_dataset(self, articles_data: List[ArticlePerformanceData]) -> pd.DataFrame:
        """分析用データセット準備"""
        print("📊 分析用データセット準備中...")
        
        records = []
        for article in articles_data:
            # 日次データを展開
            for i, (pv, users, time_on_page, bounce_rate, shares, conversions) in enumerate(
                zip(article.pv_daily, article.unique_users, article.avg_time_on_page,
                    article.bounce_rate, article.social_shares, article.conversions)
            ):
                record = {
                    # 記事属性
                    'article_id': article.article_id,
                    'title': article.title,
                    'publish_date': article.publish_date,
                    'day_since_publish': i,
                    'word_count': article.word_count,
                    'keyword_density': article.keyword_density,
                    'seo_score': article.seo_score,
                    'tone_manner': article.tone_manner,
                    'author': article.author,
                    'category': article.category,
                    
                    # パフォーマンス指標
                    'daily_pv': pv,
                    'daily_users': users,
                    'avg_time_on_page': time_on_page,
                    'bounce_rate': bounce_rate,
                    'social_shares': shares,
                    'conversions': conversions,
                    
                    # SEO指標（利用可能な場合）
                    'search_impressions': article.search_impressions[i] if i < len(article.search_impressions) else 0,
                    'search_clicks': article.search_clicks[i] if i < len(article.search_clicks) else 0,
                    'avg_position': article.avg_position[i] if i < len(article.avg_position) else 0,
                    
                    # 計算指標
                    'ctr': (article.search_clicks[i] / article.search_impressions[i]) if i < len(article.search_impressions) and article.search_impressions[i] > 0 else 0,
                    'conversion_rate': conversions / users if users > 0 else 0,
                    'engagement_score': (time_on_page * (1 - bounce_rate) * shares) if bounce_rate < 1 else 0,
                    
                    # 時間変数
                    'weekday': (article.publish_date + timedelta(days=i)).weekday(),
                    'month': (article.publish_date + timedelta(days=i)).month,
                    'is_weekend': (article.publish_date + timedelta(days=i)).weekday() >= 5,
                    
                    # タグ・フラグ（サンプル）
                    'has_images': 'images' in article.tags,
                    'has_video': 'video' in article.tags,
                    'promoted_on_social': any('social' in activity for activity in article.promotion_activities),
                    'email_promoted': any('email' in activity for activity in article.promotion_activities),
                }
                records.append(record)
        
        df = pd.DataFrame(records)
        print(f"✅ データセット準備完了: {len(df):,}行, {len(df.columns)}列")
        return df
    
    def encode_categorical_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """カテゴリ変数のエンコード"""
        categorical_columns = ['tone_manner', 'author', 'category']
        
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        return df
    
    # ============================================================
    # 1. 差分の差分法 (Difference-in-Differences)
    # ============================================================
    
    def difference_in_differences_analysis(
        self, 
        df: pd.DataFrame,
        treatment_articles: List[str],
        control_articles: List[str],
        intervention_date: datetime,
        outcome_variable: str = 'daily_pv'
    ) -> CausalInferenceResult:
        """
        差分の差分法による因果効果推定
        
        Args:
            df: 分析データ
            treatment_articles: 処置群記事ID
            control_articles: 対照群記事ID  
            intervention_date: 介入日
            outcome_variable: アウトカム変数
        """
        print(f"📈 差分の差分法分析開始: {outcome_variable}")
        
        # データ準備
        analysis_df = df[
            (df['article_id'].isin(treatment_articles + control_articles))
        ].copy()
        
        # 処置・時期ダミー変数作成
        analysis_df['treated'] = analysis_df['article_id'].isin(treatment_articles).astype(int)
        analysis_df['post_intervention'] = (analysis_df['publish_date'] >= intervention_date).astype(int)
        analysis_df['did_interaction'] = analysis_df['treated'] * analysis_df['post_intervention']
        
        # DID回帰モデル
        X = analysis_df[['treated', 'post_intervention', 'did_interaction', 'day_since_publish', 'weekday']]
        X = sm.add_constant(X)
        y = analysis_df[outcome_variable]
        
        model = sm.OLS(y, X).fit()
        
        # 結果の解釈
        did_coefficient = model.params['did_interaction']
        p_value = model.pvalues['did_interaction']
        conf_int = model.conf_int().loc['did_interaction']
        
        # 効果サイズの判定
        baseline_mean = analysis_df[
            (analysis_df['treated'] == 1) & (analysis_df['post_intervention'] == 0)
        ][outcome_variable].mean()
        
        effect_size_pct = (did_coefficient / baseline_mean) * 100 if baseline_mean > 0 else 0
        
        if abs(effect_size_pct) >= 20:
            effect_size = "大"
        elif abs(effect_size_pct) >= 10:
            effect_size = "中"
        else:
            effect_size = "小"
        
        # 結果生成
        result = CausalInferenceResult(
            method="差分の差分法 (DID)",
            treatment_effect=did_coefficient,
            confidence_interval=(conf_int[0], conf_int[1]),
            p_value=p_value,
            statistical_significance=p_value < 0.05,
            effect_size=effect_size,
            interpretation=f"介入により{outcome_variable}が{did_coefficient:.2f}単位（{effect_size_pct:.1f}%）変化",
            recommendations=self._generate_did_recommendations(did_coefficient, p_value, effect_size_pct)
        )
        
        print(f"✅ DID分析完了: 効果={did_coefficient:.2f}, p値={p_value:.4f}")
        return result
    
    def _generate_did_recommendations(self, effect: float, p_value: float, effect_size_pct: float) -> List[str]:
        """DID分析結果に基づく推奨事項生成"""
        recommendations = []
        
        if p_value < 0.05:
            if effect > 0:
                recommendations.append(f"介入により{effect_size_pct:.1f}%の有意な改善が確認されました。この施策を他の記事にも適用することを推奨します。")
                if effect_size_pct >= 20:
                    recommendations.append("効果が大きいため、類似記事への展開を優先的に検討してください。")
            else:
                recommendations.append(f"介入により{abs(effect_size_pct):.1f}%の有意な悪化が確認されました。この施策は避けることを推奨します。")
        else:
            recommendations.append("統計的に有意な効果は確認されませんでした。サンプルサイズの拡大または他の要因の検討が必要です。")
        
        return recommendations
    
    # ============================================================
    # 2. 重回帰分析
    # ============================================================
    
    def multiple_regression_analysis(
        self, 
        df: pd.DataFrame,
        target_variable: str = 'daily_pv',
        feature_columns: List[str] = None
    ) -> Dict[str, Any]:
        """
        重回帰分析による要因分析
        
        Args:
            df: 分析データ
            target_variable: 目的変数
            feature_columns: 説明変数リスト
        """
        print(f"📊 重回帰分析開始: 目的変数={target_variable}")
        
        if feature_columns is None:
            feature_columns = [
                'word_count', 'keyword_density', 'seo_score',
                'tone_manner_encoded', 'author_encoded', 'category_encoded',
                'day_since_publish', 'weekday', 'has_images', 'has_video',
                'promoted_on_social', 'email_promoted'
            ]
        
        # データ準備
        analysis_df = df.dropna(subset=[target_variable] + feature_columns).copy()
        
        X = analysis_df[feature_columns]
        y = analysis_df[target_variable]
        
        # 多重共線性チェック
        vif_data = pd.DataFrame()
        vif_data["Feature"] = X.columns
        vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(len(X.columns))]
        
        # 訓練・テストデータ分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # モデル学習
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # 予測・評価
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        
        # 統計的検定（statsmodels）
        X_sm = sm.add_constant(X)
        model_sm = sm.OLS(y, X_sm).fit()
        
        # 係数の解釈
        coefficients = pd.DataFrame({
            'feature': X.columns,
            'coefficient': model.coef_,
            'p_value': model_sm.pvalues[1:],  # 定数項を除く
            'significant': model_sm.pvalues[1:] < 0.05
        }).sort_values('coefficient', key=abs, ascending=False)
        
        # 洞察生成
        insights = self._generate_regression_insights(coefficients, target_variable)
        
        result = {
            'model_performance': {
                'r2_train': r2_train,
                'r2_test': r2_test,
                'adjusted_r2': model_sm.rsquared_adj,
                'f_statistic': model_sm.fvalue,
                'f_p_value': model_sm.f_pvalue
            },
            'coefficients': coefficients.to_dict('records'),
            'multicollinearity': vif_data.to_dict('records'),
            'feature_importance': dict(zip(X.columns, abs(model.coef_))),
            'insights': insights,
            'model_equation': self._generate_model_equation(coefficients),
            'recommendations': self._generate_regression_recommendations(coefficients, r2_test)
        }
        
        print(f"✅ 重回帰分析完了: R²={r2_test:.3f}")
        return result
    
    def _generate_regression_insights(self, coefficients: pd.DataFrame, target_variable: str) -> List[str]:
        """回帰分析結果の洞察生成"""
        insights = []
        
        # 最も影響の大きい正の要因
        positive_factors = coefficients[
            (coefficients['coefficient'] > 0) & (coefficients['significant'])
        ].head(3)
        
        if not positive_factors.empty:
            top_positive = positive_factors.iloc[0]
            insights.append(
                f"{top_positive['feature']}が{target_variable}に最も大きな正の影響を与えています"
                f"（係数: {top_positive['coefficient']:.2f}）"
            )
        
        # 最も影響の大きい負の要因
        negative_factors = coefficients[
            (coefficients['coefficient'] < 0) & (coefficients['significant'])
        ].head(3)
        
        if not negative_factors.empty:
            top_negative = negative_factors.iloc[0]
            insights.append(
                f"{top_negative['feature']}が{target_variable}に最も大きな負の影響を与えています"
                f"（係数: {top_negative['coefficient']:.2f}）"
            )
        
        # 有意でない要因
        non_significant = coefficients[~coefficients['significant']]
        if len(non_significant) > 0:
            insights.append(f"{len(non_significant)}個の要因は統計的に有意な影響を示していません")
        
        return insights
    
    def _generate_model_equation(self, coefficients: pd.DataFrame) -> str:
        """モデル方程式の生成"""
        terms = []
        for _, row in coefficients.iterrows():
            coef = row['coefficient']
            feature = row['feature']
            if coef >= 0:
                terms.append(f"+{coef:.3f}*{feature}")
            else:
                terms.append(f"{coef:.3f}*{feature}")
        
        equation = "予測値 = 定数項 " + " ".join(terms)
        return equation
    
    def _generate_regression_recommendations(self, coefficients: pd.DataFrame, r2: float) -> List[str]:
        """回帰分析に基づく推奨事項"""
        recommendations = []
        
        if r2 >= 0.7:
            recommendations.append("モデルの説明力が高く、要因分析の信頼性があります。")
        elif r2 >= 0.5:
            recommendations.append("モデルの説明力は中程度です。追加の説明変数の検討を推奨します。")
        else:
            recommendations.append("モデルの説明力が低いです。データの質や変数選択の見直しが必要です。")
        
        # 有意な正の要因に基づく推奨
        significant_positive = coefficients[
            (coefficients['coefficient'] > 0) & (coefficients['significant'])
        ]
        
        for _, factor in significant_positive.head(3).iterrows():
            recommendations.append(
                f"{factor['feature']}を向上させることで{factor['coefficient']:.2f}の改善効果が期待できます"
            )
        
        return recommendations
    
    # ============================================================
    # 3. クラスター分析
    # ============================================================
    
    def cluster_analysis(
        self, 
        df: pd.DataFrame,
        feature_columns: List[str] = None,
        n_clusters: int = None
    ) -> Dict[str, Any]:
        """
        クラスター分析による記事パターン分類
        
        Args:
            df: 分析データ
            feature_columns: クラスタリング用特徴量
            n_clusters: クラスター数（Noneの場合は自動決定）
        """
        print("🎯 クラスター分析開始")
        
        if feature_columns is None:
            feature_columns = [
                'word_count', 'keyword_density', 'seo_score',
                'daily_pv', 'avg_time_on_page', 'bounce_rate',
                'social_shares', 'conversions', 'conversion_rate'
            ]
        
        # データ準備
        analysis_df = df.dropna(subset=feature_columns).copy()
        
        # 特徴量標準化
        X = self.scaler.fit_transform(analysis_df[feature_columns])
        
        # 最適クラスター数の決定（エルボー法 + シルエット分析）
        if n_clusters is None:
            n_clusters = self._find_optimal_clusters(X)
        
        # K-meansクラスタリング
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        
        # クラスター結果をデータフレームに追加
        analysis_df['cluster'] = cluster_labels
        
        # 各クラスターの特徴分析
        cluster_profiles = self._analyze_cluster_profiles(analysis_df, feature_columns)
        
        # クラスター品質評価
        silhouette_avg = silhouette_score(X, cluster_labels)
        
        # DBSCANによる異常値検出も実行
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        dbscan_labels = dbscan.fit_predict(X)
        outliers = np.sum(dbscan_labels == -1)
        
        result = {
            'n_clusters': n_clusters,
            'silhouette_score': silhouette_avg,
            'cluster_profiles': cluster_profiles,
            'outliers_detected': outliers,
            'cluster_assignments': dict(zip(analysis_df['article_id'], cluster_labels)),
            'cluster_insights': self._generate_cluster_insights(cluster_profiles),
            'recommendations': self._generate_cluster_recommendations(cluster_profiles)
        }
        
        print(f"✅ クラスター分析完了: {n_clusters}クラスター, シルエット係数={silhouette_avg:.3f}")
        return result
    
    def _find_optimal_clusters(self, X: np.ndarray, max_clusters: int = 10) -> int:
        """最適クラスター数の決定"""
        inertias = []
        silhouette_scores = []
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, labels))
        
        # シルエット係数が最大となるクラスター数を選択
        optimal_k = np.argmax(silhouette_scores) + 2
        return optimal_k
    
    def _analyze_cluster_profiles(self, df: pd.DataFrame, feature_columns: List[str]) -> Dict[int, Dict]:
        """各クラスターのプロファイル分析"""
        cluster_profiles = {}
        
        for cluster_id in sorted(df['cluster'].unique()):
            cluster_data = df[df['cluster'] == cluster_id]
            
            profile = {
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(df) * 100,
                'feature_means': cluster_data[feature_columns].mean().to_dict(),
                'feature_stds': cluster_data[feature_columns].std().to_dict(),
                'top_articles': cluster_data.nlargest(5, 'daily_pv')['article_id'].tolist(),
                'common_characteristics': self._identify_cluster_characteristics(cluster_data, feature_columns)
            }
            
            cluster_profiles[cluster_id] = profile
        
        return cluster_profiles
    
    def _identify_cluster_characteristics(self, cluster_data: pd.DataFrame, feature_columns: List[str]) -> List[str]:
        """クラスターの特徴的な性質を特定"""
        characteristics = []
        
        # 全体平均と比較
        overall_means = cluster_data[feature_columns].mean()
        
        # 特に高い・低い特徴量を特定
        for feature in feature_columns:
            cluster_mean = cluster_data[feature].mean()
            
            if cluster_mean > overall_means[feature] * 1.2:
                characteristics.append(f"{feature}が高い")
            elif cluster_mean < overall_means[feature] * 0.8:
                characteristics.append(f"{feature}が低い")
        
        return characteristics
    
    def _generate_cluster_insights(self, cluster_profiles: Dict[int, Dict]) -> List[str]:
        """クラスター分析の洞察生成"""
        insights = []
        
        # 最大・最小クラスターの特定
        cluster_sizes = {k: v['size'] for k, v in cluster_profiles.items()}
        largest_cluster = max(cluster_sizes, key=cluster_sizes.get)
        smallest_cluster = min(cluster_sizes, key=cluster_sizes.get)
        
        insights.append(f"クラスター{largest_cluster}が最大（{cluster_sizes[largest_cluster]}記事, {cluster_profiles[largest_cluster]['percentage']:.1f}%）")
        insights.append(f"クラスター{smallest_cluster}が最小（{cluster_sizes[smallest_cluster]}記事, {cluster_profiles[smallest_cluster]['percentage']:.1f}%）")
        
        # 高パフォーマンスクラスターの特定
        avg_pvs = {k: v['feature_means'].get('daily_pv', 0) for k, v in cluster_profiles.items()}
        best_cluster = max(avg_pvs, key=avg_pvs.get)
        
        insights.append(f"クラスター{best_cluster}が最高パフォーマンス（平均PV: {avg_pvs[best_cluster]:.0f}）")
        insights.append(f"高パフォーマンス記事の特徴: {', '.join(cluster_profiles[best_cluster]['common_characteristics'])}")
        
        return insights
    
    def _generate_cluster_recommendations(self, cluster_profiles: Dict[int, Dict]) -> List[str]:
        """クラスター分析に基づく推奨事項"""
        recommendations = []
        
        # 高パフォーマンスクラスターの特徴を他に適用
        avg_pvs = {k: v['feature_means'].get('daily_pv', 0) for k, v in cluster_profiles.items()}
        best_cluster = max(avg_pvs, key=avg_pvs.get)
        best_characteristics = cluster_profiles[best_cluster]['common_characteristics']
        
        recommendations.append(f"クラスター{best_cluster}の特徴（{', '.join(best_characteristics)}）を他の記事にも適用することを推奨します。")
        
        # 低パフォーマンスクラスターの改善提案
        worst_cluster = min(avg_pvs, key=avg_pvs.get)
        worst_characteristics = cluster_profiles[worst_cluster]['common_characteristics']
        
        recommendations.append(f"クラスター{worst_cluster}の記事は改善が必要です。特に{', '.join(worst_characteristics)}の見直しを検討してください。")
        
        # バランスの取れた戦略提案
        recommendations.append("異なるクラスターの成功要因を組み合わせた記事戦略を検討してください。")
        
        return recommendations
    
    # ============================================================
    # 4. 時系列分析
    # ============================================================
    
    def time_series_analysis(
        self, 
        df: pd.DataFrame,
        date_column: str = 'publish_date',
        value_column: str = 'daily_pv',
        article_id: str = None
    ) -> Dict[str, Any]:
        """
        時系列分析（季節性・トレンド分解）
        
        Args:
            df: 分析データ
            date_column: 日付列
            value_column: 分析対象値
            article_id: 特定記事ID（Noneの場合は全体分析）
        """
        print(f"📈 時系列分析開始: {value_column}")
        
        # データ準備
        if article_id:
            analysis_df = df[df['article_id'] == article_id].copy()
        else:
            # 全記事の日次集計
            analysis_df = df.groupby(date_column)[value_column].sum().reset_index()
        
        analysis_df = analysis_df.sort_values(date_column)
        
        # 時系列データ作成
        ts_data = analysis_df.set_index(date_column)[value_column]
        
        # 季節性分解（週次パターン）
        if len(ts_data) >= 14:  # 最低2週間のデータが必要
            decomposition = seasonal_decompose(ts_data, model='additive', period=7)
            
            trend = decomposition.trend.dropna()
            seasonal = decomposition.seasonal.dropna()
            residual = decomposition.resid.dropna()
        else:
            trend = seasonal = residual = ts_data
        
        # トレンド分析
        if len(trend) > 1:
            trend_slope, trend_intercept, trend_r, trend_p, trend_stderr = stats.linregress(
                range(len(trend)), trend.values
            )
            
            if trend_p < 0.05:
                if trend_slope > 0:
                    trend_direction = "上昇トレンド"
                else:
                    trend_direction = "下降トレンド"
            else:
                trend_direction = "明確なトレンドなし"
        else:
            trend_slope = trend_intercept = trend_r = trend_p = 0
            trend_direction = "データ不足"
        
        # 季節性パターン分析
        if len(seasonal) >= 7:
            weekday_patterns = {}
            for i in range(7):
                weekday_data = seasonal.iloc[i::7]
                if len(weekday_data) > 0:
                    weekday_patterns[i] = weekday_data.mean()
            
            best_weekday = max(weekday_patterns, key=weekday_patterns.get)
            worst_weekday = min(weekday_patterns, key=weekday_patterns.get)
        else:
            weekday_patterns = {}
            best_weekday = worst_weekday = 0
        
        # 異常値検出
        if len(residual) > 0:
            residual_mean = residual.mean()
            residual_std = residual.std()
            anomalies = residual[abs(residual - residual_mean) > 2 * residual_std]
        else:
            anomalies = pd.Series([])
        
        result = {
            'trend_analysis': {
                'direction': trend_direction,
                'slope': trend_slope,
                'r_squared': trend_r ** 2,
                'p_value': trend_p,
                'significance': trend_p < 0.05
            },
            'seasonal_patterns': {
                'weekday_effects': weekday_patterns,
                'best_weekday': best_weekday,
                'worst_weekday': worst_weekday,
                'seasonality_strength': seasonal.std() / ts_data.std() if len(seasonal) > 0 else 0
            },
            'anomaly_detection': {
                'anomaly_count': len(anomalies),
                'anomaly_dates': anomalies.index.tolist(),
                'anomaly_values': anomalies.values.tolist()
            },
            'summary_statistics': {
                'mean': ts_data.mean(),
                'std': ts_data.std(),
                'min': ts_data.min(),
                'max': ts_data.max(),
                'total_observations': len(ts_data)
            },
            'insights': self._generate_timeseries_insights(trend_direction, weekday_patterns, len(anomalies)),
            'recommendations': self._generate_timeseries_recommendations(trend_direction, best_weekday, worst_weekday)
        }
        
        print(f"✅ 時系列分析完了: {trend_direction}")
        return result
    
    def _generate_timeseries_insights(self, trend_direction: str, weekday_patterns: Dict, anomaly_count: int) -> List[str]:
        """時系列分析の洞察生成"""
        insights = []
        
        insights.append(f"全体的な傾向: {trend_direction}")
        
        if weekday_patterns:
            weekday_names = ['月', '火', '水', '木', '金', '土', '日']
            best_day = max(weekday_patterns, key=weekday_patterns.get)
            worst_day = min(weekday_patterns, key=weekday_patterns.get)
            
            insights.append(f"最もパフォーマンスが高い曜日: {weekday_names[best_day]}曜日")
            insights.append(f"最もパフォーマンスが低い曜日: {weekday_names[worst_day]}曜日")
        
        if anomaly_count > 0:
            insights.append(f"{anomaly_count}個の異常値が検出されました")
        
        return insights
    
    def _generate_timeseries_recommendations(self, trend_direction: str, best_weekday: int, worst_weekday: int) -> List[str]:
        """時系列分析に基づく推奨事項"""
        recommendations = []
        
        weekday_names = ['月', '火', '水', '木', '金', '土', '日']
        
        if "上昇" in trend_direction:
            recommendations.append("パフォーマンスが向上しています。現在の戦略を継続することを推奨します。")
        elif "下降" in trend_direction:
            recommendations.append("パフォーマンスが低下しています。戦略の見直しが必要です。")
        
        if best_weekday is not None:
            recommendations.append(f"{weekday_names[best_weekday]}曜日の公開・プロモーションを優先することを推奨します。")
        
        if worst_weekday is not None:
            recommendations.append(f"{weekday_names[worst_weekday]}曜日は避けるか、特別な施策を検討してください。")
        
        return recommendations
    
    # ============================================================
    # 5. 統合分析レポート生成
    # ============================================================
    
    def generate_comprehensive_analysis_report(
        self, 
        articles_data: List[ArticlePerformanceData],
        target_variable: str = 'daily_pv'
    ) -> Dict[str, Any]:
        """包括的分析レポート生成"""
        print("📋 包括的分析レポート生成開始")
        print("=" * 50)
        
        # データセット準備
        df = self.prepare_analysis_dataset(articles_data)
        df = self.encode_categorical_variables(df)
        
        # 各種分析実行
        regression_results = self.multiple_regression_analysis(df, target_variable)
        cluster_results = self.cluster_analysis(df)
        timeseries_results = self.time_series_analysis(df, value_column=target_variable)
        
        # 統合洞察生成
        integrated_insights = self._generate_integrated_insights(
            regression_results, cluster_results, timeseries_results
        )
        
        # 包括的推奨事項
        comprehensive_recommendations = self._generate_comprehensive_recommendations(
            regression_results, cluster_results, timeseries_results
        )
        
        report = {
            'executive_summary': {
                'total_articles_analyzed': len(set(df['article_id'])),
                'analysis_period': f"{df['publish_date'].min()} 〜 {df['publish_date'].max()}",
                'key_findings': integrated_insights[:5],
                'priority_recommendations': comprehensive_recommendations[:3]
            },
            'regression_analysis': regression_results,
            'cluster_analysis': cluster_results,
            'time_series_analysis': timeseries_results,
            'integrated_insights': integrated_insights,
            'comprehensive_recommendations': comprehensive_recommendations,
            'data_quality_assessment': self._assess_data_quality(df),
            'methodology_notes': self._generate_methodology_notes()
        }
        
        print("✅ 包括的分析レポート生成完了")
        return report
    
    def _generate_integrated_insights(self, regression_results: Dict, cluster_results: Dict, timeseries_results: Dict) -> List[str]:
        """統合洞察生成"""
        insights = []
        
        # 回帰分析からの主要知見
        if regression_results['coefficients']:
            top_factor = max(regression_results['coefficients'], key=lambda x: abs(x['coefficient']))
            insights.append(f"最も重要な要因: {top_factor['feature']}（係数: {top_factor['coefficient']:.3f}）")
        
        # クラスター分析からの知見
        if cluster_results['cluster_insights']:
            insights.extend(cluster_results['cluster_insights'][:2])
        
        # 時系列分析からの知見
        if timeseries_results['insights']:
            insights.extend(timeseries_results['insights'][:2])
        
        # 相互関係の洞察
        if regression_results['model_performance']['r2_test'] > 0.5 and cluster_results['silhouette_score'] > 0.3:
            insights.append("回帰分析とクラスター分析の両方で有意な結果が得られており、分析の信頼性が高いです。")
        
        return insights
    
    def _generate_comprehensive_recommendations(self, regression_results: Dict, cluster_results: Dict, timeseries_results: Dict) -> List[str]:
        """包括的推奨事項生成"""
        recommendations = []
        
        # 回帰分析からの推奨事項
        if regression_results['recommendations']:
            recommendations.extend(regression_results['recommendations'][:2])
        
        # クラスター分析からの推奨事項
        if cluster_results['recommendations']:
            recommendations.extend(cluster_results['recommendations'][:2])
        
        # 時系列分析からの推奨事項
        if timeseries_results['recommendations']:
            recommendations.extend(timeseries_results['recommendations'][:2])
        
        # 統合的な推奨事項
        recommendations.append("各分析手法の結果を総合的に検討し、段階的な改善計画を策定することを推奨します。")
        recommendations.append("継続的なモニタリングとフィードバックループの構築により、データドリブンな記事戦略を実現してください。")
        
        return recommendations
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """データ品質評価"""
        return {
            'completeness': {
                'total_records': len(df),
                'missing_values': df.isnull().sum().to_dict(),
                'completeness_rate': (1 - df.isnull().sum() / len(df)).to_dict()
            },
            'consistency': {
                'duplicate_records': df.duplicated().sum(),
                'data_types': df.dtypes.to_dict()
            },
            'validity': {
                'negative_values': (df.select_dtypes(include=[np.number]) < 0).sum().to_dict(),
                'outliers_detected': self._detect_outliers(df)
            }
        }
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, int]:
        """外れ値検出"""
        outliers = {}
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers[col] = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        
        return outliers
    
    def _generate_methodology_notes(self) -> List[str]:
        """方法論ノート生成"""
        return [
            "差分の差分法（DID）: 処置群と対照群の時系列変化を比較して因果効果を推定",
            "重回帰分析: 複数の説明変数がアウトカムに与える影響を定量化",
            "クラスター分析: K-means法を用いて記事をパフォーマンスパターンで分類",
            "時系列分析: 季節性分解によりトレンド・季節性・異常値を特定",
            "多重共線性: VIF値による説明変数間の相関関係を評価",
            "統計的有意性: p値0.05を基準とした統計的検定を実施"
        ]


# ============================================================
# サンプル使用例
# ============================================================

if __name__ == "__main__":
    # サンプルデータ生成（実際の使用時はDBから取得）
    sample_articles = [
        ArticlePerformanceData(
            article_id="article_001",
            title="誕生花完全ガイド",
            publish_date=datetime(2024, 1, 1),
            word_count=5000,
            keyword_density=0.02,
            seo_score=85,
            tone_manner="formal",
            author="author_a",
            category="gardening",
            pv_daily=[100, 150, 200, 180, 220, 190, 160] * 10,
            unique_users=[80, 120, 160, 144, 176, 152, 128] * 10,
            avg_time_on_page=[3.5, 4.0, 4.2, 3.8, 4.5, 4.1, 3.7] * 10,
            bounce_rate=[0.3, 0.25, 0.2, 0.28, 0.18, 0.22, 0.32] * 10,
            social_shares=[5, 8, 12, 10, 15, 11, 7] * 10,
            conversions=[2, 3, 5, 4, 6, 4, 3] * 10,
            search_impressions=[1000, 1200, 1500, 1300, 1600, 1400, 1100] * 10,
            search_clicks=[50, 70, 90, 80, 100, 85, 65] * 10,
            avg_position=[8.5, 7.2, 6.1, 6.8, 5.9, 6.5, 7.8] * 10,
            tags=["images", "comprehensive"],
            promotion_activities=["social_media", "email"],
            external_events=[]
        )
    ]
    
    # 分析実行
    analyzer = AdvancedStatisticalAnalyzer()
    report = analyzer.generate_comprehensive_analysis_report(sample_articles)
    
    print("\n📊 分析結果サマリー:")
    print(f"分析記事数: {report['executive_summary']['total_articles_analyzed']}")
    print(f"主要知見: {report['executive_summary']['key_findings'][0]}")
    print(f"優先推奨事項: {report['executive_summary']['priority_recommendations'][0]}")