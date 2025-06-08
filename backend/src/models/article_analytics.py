#!/usr/bin/env python3
"""
記事分析用データモデル
タギングシステム・パフォーマンス追跡・統計分析用のSQLAlchemyモデル
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from .base import Base


class ArticleTag(Base):
    """記事タグテーブル"""
    __tablename__ = "article_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    tag_type = Column(String(50), nullable=False)  # performance, content, seo, experiment
    tag_name = Column(String(100), nullable=False)
    tag_value = Column(String(200))
    confidence_score = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))
    
    # リレーションシップ
    article = relationship("Article", back_populates="tags")
    
    # インデックス
    __table_args__ = (
        Index('idx_article_tag_type', 'article_id', 'tag_type'),
        Index('idx_tag_name', 'tag_name'),
    )


class ArticlePerformanceMetrics(Base):
    """記事パフォーマンス指標テーブル"""
    __tablename__ = "article_performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # トラフィック指標
    page_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    sessions = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)  # 秒
    bounce_rate = Column(Float, default=0.0)  # 0-1
    pages_per_session = Column(Float, default=0.0)
    
    # エンゲージメント指標
    avg_time_on_page = Column(Float, default=0.0)  # 秒
    scroll_depth_avg = Column(Float, default=0.0)  # 0-1
    internal_link_clicks = Column(Integer, default=0)
    external_link_clicks = Column(Integer, default=0)
    
    # ソーシャル指標
    social_shares_total = Column(Integer, default=0)
    facebook_shares = Column(Integer, default=0)
    twitter_shares = Column(Integer, default=0)
    linkedin_shares = Column(Integer, default=0)
    
    # コンバージョン指標
    conversions_total = Column(Integer, default=0)
    email_signups = Column(Integer, default=0)
    contact_form_submissions = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    purchases = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # SEO指標
    search_impressions = Column(Integer, default=0)
    search_clicks = Column(Integer, default=0)
    search_ctr = Column(Float, default=0.0)  # 0-1
    avg_search_position = Column(Float, default=0.0)
    
    # 計算指標
    conversion_rate = Column(Float, default=0.0)  # conversions / unique_visitors
    engagement_score = Column(Float, default=0.0)  # カスタム計算スコア
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    article = relationship("Article", back_populates="performance_metrics")
    
    # インデックス
    __table_args__ = (
        Index('idx_article_date', 'article_id', 'date'),
        Index('idx_performance_date', 'date'),
    )


class ArticleExperiment(Base):
    """記事A/Bテスト・実験テーブル"""
    __tablename__ = "article_experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String(200), nullable=False)
    experiment_type = Column(String(50), nullable=False)  # ab_test, multivariate, etc.
    description = Column(Text)
    
    # 実験設定
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    status = Column(String(20), default='active')  # active, completed, paused, cancelled
    
    # 統計設定
    significance_level = Column(Float, default=0.05)
    power = Column(Float, default=0.8)
    minimum_detectable_effect = Column(Float, default=0.1)
    
    # メタデータ
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    experiment_articles = relationship("ArticleExperimentAssignment", back_populates="experiment")


class ArticleExperimentAssignment(Base):
    """記事実験割り当てテーブル"""
    __tablename__ = "article_experiment_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("article_experiments.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # 実験グループ
    treatment_group = Column(String(50), nullable=False)  # control, treatment_a, treatment_b, etc.
    assignment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # 実験変数
    variables_modified = Column(JSON)  # {"title": "new_title", "meta_description": "new_desc"}
    
    # リレーションシップ
    experiment = relationship("ArticleExperiment", back_populates="experiment_articles")
    article = relationship("Article")
    
    # インデックス
    __table_args__ = (
        Index('idx_experiment_article', 'experiment_id', 'article_id'),
    )


class ArticleAnalysisResult(Base):
    """記事分析結果テーブル"""
    __tablename__ = "article_analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # regression, cluster, time_series, causal_inference
    analysis_version = Column(String(20), default='1.0')
    
    # 分析設定
    analysis_parameters = Column(JSON)  # 分析実行時のパラメータ
    feature_columns = Column(JSON)  # 使用した特徴量
    target_variable = Column(String(50))  # 目的変数
    
    # 分析結果
    results = Column(JSON, nullable=False)  # 分析結果の詳細データ
    model_performance = Column(JSON)  # モデル性能指標
    insights = Column(JSON)  # 洞察・発見事項
    recommendations = Column(JSON)  # 推奨事項
    
    # 統計情報
    statistical_significance = Column(Boolean, default=False)
    confidence_level = Column(Float, default=0.95)
    effect_size = Column(Float)
    p_value = Column(Float)
    
    # メタデータ
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    analyst = Column(String(100))
    data_period_start = Column(DateTime(timezone=True))
    data_period_end = Column(DateTime(timezone=True))
    sample_size = Column(Integer)
    
    # リレーションシップ
    article = relationship("Article")
    
    # インデックス
    __table_args__ = (
        Index('idx_article_analysis_type', 'article_id', 'analysis_type'),
        Index('idx_analysis_date', 'analysis_date'),
    )


class ArticleComparison(Base):
    """記事比較分析テーブル"""
    __tablename__ = "article_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    comparison_name = Column(String(200), nullable=False)
    comparison_type = Column(String(50), nullable=False)  # performance, content, seo
    
    # 比較対象記事
    primary_article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    comparison_articles = Column(JSON)  # [article_id1, article_id2, ...]
    
    # 比較設定
    comparison_metrics = Column(JSON)  # 比較する指標リスト
    time_period_days = Column(Integer, default=30)
    
    # 比較結果
    results = Column(JSON)
    insights = Column(JSON)
    recommendations = Column(JSON)
    
    # 統計テスト結果
    statistical_tests = Column(JSON)  # t-test, chi-square, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))
    
    # リレーションシップ
    primary_article = relationship("Article", foreign_keys=[primary_article_id])


class ArticlePerformancePrediction(Base):
    """記事パフォーマンス予測テーブル"""
    __tablename__ = "article_performance_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # 予測設定
    prediction_model = Column(String(50), nullable=False)  # linear_regression, random_forest, etc.
    model_version = Column(String(20), default='1.0')
    features_used = Column(JSON)
    
    # 予測期間
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    prediction_period_days = Column(Integer, default=30)
    target_date = Column(DateTime(timezone=True))
    
    # 予測結果
    predicted_page_views = Column(Integer)
    predicted_conversions = Column(Integer)
    predicted_engagement_score = Column(Float)
    predicted_search_ranking = Column(Float)
    
    # 信頼区間
    pv_confidence_lower = Column(Integer)
    pv_confidence_upper = Column(Integer)
    conversion_confidence_lower = Column(Integer)
    conversion_confidence_upper = Column(Integer)
    
    # モデル性能
    model_accuracy = Column(Float)  # R²やMAPE等
    prediction_confidence = Column(Float, default=0.8)
    
    # 実績との比較（予測期間後に更新）
    actual_page_views = Column(Integer)
    actual_conversions = Column(Integer)
    actual_engagement_score = Column(Float)
    prediction_error = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # リレーションシップ
    article = relationship("Article")
    
    # インデックス
    __table_args__ = (
        Index('idx_article_prediction_date', 'article_id', 'prediction_date'),
        Index('idx_target_date', 'target_date'),
    )


class ContentAnalysisMetadata(Base):
    """コンテンツ分析メタデータテーブル"""
    __tablename__ = "content_analysis_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # コンテンツ特性
    reading_level = Column(String(20))  # elementary, middle_school, high_school, college
    sentiment_score = Column(Float)  # -1 to 1
    formality_score = Column(Float)  # 0 to 1
    complexity_score = Column(Float)  # 0 to 1
    
    # 構造分析
    paragraph_count = Column(Integer, default=0)
    sentence_count = Column(Integer, default=0)
    avg_sentence_length = Column(Float, default=0.0)
    heading_count = Column(JSON)  # {"h1": 1, "h2": 5, "h3": 12}
    
    # キーワード分析
    keyword_density_primary = Column(Float, default=0.0)
    keyword_density_secondary = Column(Float, default=0.0)
    keyword_distribution = Column(JSON)  # キーワードの分布情報
    
    # 画像・メディア分析
    image_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    has_featured_image = Column(Boolean, default=False)
    media_alt_text_coverage = Column(Float, default=0.0)  # 0-1
    
    # リンク分析
    internal_link_count = Column(Integer, default=0)
    external_link_count = Column(Integer, default=0)
    broken_link_count = Column(Integer, default=0)
    
    # SEO分析
    meta_description_length = Column(Integer, default=0)
    title_seo_score = Column(Float, default=0.0)
    url_seo_score = Column(Float, default=0.0)
    schema_markup_present = Column(Boolean, default=False)
    
    # 更新情報
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    analyzer_version = Column(String(20), default='1.0')
    
    # リレーションシップ
    article = relationship("Article")
    
    # インデックス
    __table_args__ = (
        Index('idx_content_analysis_date', 'article_id', 'analysis_date'),
    )


class PerformanceAlert(Base):
    """パフォーマンスアラートテーブル"""
    __tablename__ = "performance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # アラート設定
    alert_type = Column(String(50), nullable=False)  # performance_drop, anomaly, threshold
    metric_name = Column(String(50), nullable=False)
    threshold_value = Column(Float)
    condition = Column(String(20))  # above, below, change_percent
    
    # アラート状態
    status = Column(String(20), default='active')  # active, acknowledged, resolved, disabled
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # アラート詳細
    current_value = Column(Float)
    previous_value = Column(Float)
    change_percent = Column(Float)
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    
    # 対応情報
    acknowledged_by = Column(String(100))
    resolution_notes = Column(Text)
    action_taken = Column(JSON)  # 実施した対応策
    
    # リレーションシップ
    article = relationship("Article")
    
    # インデックス
    __table_args__ = (
        Index('idx_alert_status', 'status', 'triggered_at'),
        Index('idx_article_alerts', 'article_id', 'status'),
    )


# 既存のArticleモデルにリレーションシップを追加
# 注意: 実際の実装では既存のmodels/article.pyを更新する必要があります

"""
以下を既存のArticleモデルに追加:

# 分析関連のリレーションシップ
tags = relationship("ArticleTag", back_populates="article", cascade="all, delete-orphan")
performance_metrics = relationship("ArticlePerformanceMetrics", back_populates="article", cascade="all, delete-orphan")
analysis_results = relationship("ArticleAnalysisResult", cascade="all, delete-orphan")
predictions = relationship("ArticlePerformancePrediction", cascade="all, delete-orphan")
content_metadata = relationship("ContentAnalysisMetadata", cascade="all, delete-orphan")
alerts = relationship("PerformanceAlert", cascade="all, delete-orphan")

# メソッド追加例
def get_latest_performance(self, days: int = 30) -> Optional[Dict[str, Any]]:
    \"\"\"最新のパフォーマンス指標を取得\"\"\"
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    
    metrics = [m for m in self.performance_metrics if m.date >= cutoff_date]
    if not metrics:
        return None
    
    # 集計処理
    total_pv = sum(m.page_views for m in metrics)
    avg_time = sum(m.avg_time_on_page for m in metrics) / len(metrics)
    # ... 他の指標も計算
    
    return {
        'total_page_views': total_pv,
        'avg_time_on_page': avg_time,
        # ... 他の指標
    }

def get_performance_trend(self, metric: str, days: int = 30) -> List[Tuple[datetime, float]]:
    \"\"\"指定指標のトレンドデータを取得\"\"\"
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    
    metrics = [(m.date, getattr(m, metric, 0)) for m in self.performance_metrics 
               if m.date >= cutoff_date]
    return sorted(metrics, key=lambda x: x[0])

def add_tag(self, tag_type: str, tag_name: str, tag_value: str = None, confidence: float = 1.0):
    \"\"\"記事にタグを追加\"\"\"
    tag = ArticleTag(
        article_id=self.id,
        tag_type=tag_type,
        tag_name=tag_name,
        tag_value=tag_value,
        confidence_score=confidence
    )
    self.tags.append(tag)
    return tag

def get_tags_by_type(self, tag_type: str) -> List[ArticleTag]:
    \"\"\"タイプ別のタグを取得\"\"\"
    return [tag for tag in self.tags if tag.tag_type == tag_type]
"""


# ============================================================
# データベース初期化・マイグレーション用ヘルパー
# ============================================================

def create_analytics_tables(engine):
    """分析用テーブル作成"""
    Base.metadata.create_all(bind=engine)
    print("✅ 分析用テーブル作成完了")


def create_sample_performance_data(session, article_id: int, days: int = 30):
    """サンプルパフォーマンスデータ作成"""
    import random
    from datetime import datetime, timedelta
    
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        current_date = base_date + timedelta(days=i)
        
        # ランダムなパフォーマンスデータ生成
        metrics = ArticlePerformanceMetrics(
            article_id=article_id,
            date=current_date,
            page_views=random.randint(50, 500),
            unique_visitors=random.randint(40, 400),
            sessions=random.randint(35, 350),
            avg_session_duration=random.uniform(60, 300),
            bounce_rate=random.uniform(0.2, 0.8),
            pages_per_session=random.uniform(1.1, 3.5),
            avg_time_on_page=random.uniform(30, 180),
            scroll_depth_avg=random.uniform(0.3, 0.9),
            internal_link_clicks=random.randint(0, 20),
            external_link_clicks=random.randint(0, 10),
            social_shares_total=random.randint(0, 50),
            conversions_total=random.randint(0, 15),
            search_impressions=random.randint(100, 2000),
            search_clicks=random.randint(5, 100),
            search_ctr=random.uniform(0.02, 0.15),
            avg_search_position=random.uniform(3, 20)
        )
        
        # 計算指標を設定
        if metrics.unique_visitors > 0:
            metrics.conversion_rate = metrics.conversions_total / metrics.unique_visitors
        
        metrics.engagement_score = (
            metrics.avg_time_on_page * 
            (1 - metrics.bounce_rate) * 
            metrics.scroll_depth_avg
        )
        
        session.add(metrics)
    
    session.commit()
    print(f"✅ {days}日分のサンプルパフォーマンスデータ作成完了")


def add_sample_tags(session, article_id: int):
    """サンプルタグデータ追加"""
    sample_tags = [
        ("performance", "high_traffic", "top_10_percent", 0.95),
        ("content", "comprehensive", "5000_plus_words", 1.0),
        ("seo", "keyword_optimized", "primary_density_optimal", 0.85),
        ("experiment", "ab_test_title", "version_b", 1.0),
        ("content", "tone_formal", "professional", 0.9),
        ("performance", "high_engagement", "above_average", 0.8),
        ("seo", "featured_snippet", "position_0_candidate", 0.7),
        ("content", "has_images", "10_plus_images", 1.0),
        ("promotion", "social_shared", "viral_potential", 0.6),
        ("technical", "fast_loading", "under_3_seconds", 0.9)
    ]
    
    for tag_type, tag_name, tag_value, confidence in sample_tags:
        tag = ArticleTag(
            article_id=article_id,
            tag_type=tag_type,
            tag_name=tag_name,
            tag_value=tag_value,
            confidence_score=confidence
        )
        session.add(tag)
    
    session.commit()
    print("✅ サンプルタグデータ追加完了")


if __name__ == "__main__":
    print("📊 記事分析用データモデル定義完了")
    print("主な機能:")
    print("- 記事タギングシステム")
    print("- パフォーマンス指標追跡")
    print("- A/Bテスト・実験管理")
    print("- 分析結果保存")
    print("- 予測結果管理")
    print("- コンテンツ分析メタデータ")
    print("- パフォーマンスアラート")