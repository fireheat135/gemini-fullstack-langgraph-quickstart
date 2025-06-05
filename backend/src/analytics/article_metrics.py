#!/usr/bin/env python3
"""
Article Metrics Data Model
記事メトリクスデータモデル

記事のパフォーマンスデータと属性タグを管理するデータクラス
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToneStyle(str, Enum):
    """トーンスタイル分類"""
    FRIENDLY = "親しみやすい"
    PROFESSIONAL = "専門的"
    CASUAL = "カジュアル"
    FORMAL = "フォーマル"
    CONVERSATIONAL = "会話調"
    AUTHORITATIVE = "権威的"


class WritingFormality(str, Enum):
    """文体の丁寧さ分類"""
    POLITE = "丁寧語"
    DESU_MASU = "です・ます調"
    DA_DEARU = "だ・である調"
    CASUAL_FORM = "くだけた調"


class TargetAudience(str, Enum):
    """ターゲットオーディエンス分類"""
    BEGINNER = "初心者"
    INTERMEDIATE = "中級者"
    EXPERT = "専門家"
    GENERAL = "一般読者"


class EmotionalTone(str, Enum):
    """感情的トーン分類"""
    POSITIVE = "ポジティブ"
    NEUTRAL = "ニュートラル"
    WARM = "親近感"
    ENCOURAGING = "励まし"
    INFORMATIVE = "情報的"


@dataclass
class ArticleMetrics:
    """記事メトリクスデータクラス"""
    
    # 基本情報
    article_id: int
    title: str
    word_count: int
    character_count: int
    paragraph_count: int
    
    # SEO関連タグ
    primary_keyword: str
    keyword_density: float
    seo_keywords: List[str] = field(default_factory=list)
    keyword_volumes: Dict[str, int] = field(default_factory=dict)  # キーワード別検索ボリューム
    semantic_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    
    # 構造タグ
    h1_count: int = 0
    h2_count: int = 0
    h3_count: int = 0
    image_count: int = 0
    internal_link_count: int = 0
    external_link_count: int = 0
    list_count: int = 0  # リスト要素数
    table_count: int = 0  # テーブル数
    
    # トンマナタグ
    tone_style: ToneStyle = ToneStyle.FRIENDLY
    writing_formality: WritingFormality = WritingFormality.DESU_MASU
    target_audience: TargetAudience = TargetAudience.GENERAL
    emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL
    
    # 可読性指標
    readability_score: float = 0.0  # 可読性スコア (0-100)
    average_sentence_length: float = 0.0  # 平均文長
    complex_word_ratio: float = 0.0  # 複雑語彙率
    
    # パフォーマンス指標
    page_views: int = 0
    unique_visitors: int = 0
    average_time_on_page: float = 0.0  # 秒
    bounce_rate: float = 0.0  # 直帰率 (0-1)
    conversion_rate: float = 0.0  # コンバージョン率 (0-1)
    organic_traffic_rate: float = 0.0  # オーガニック流入率 (0-1)
    social_shares: int = 0
    backlink_count: int = 0
    
    # 検索エンジン関連
    average_search_position: float = 0.0  # 平均検索順位
    click_through_rate: float = 0.0  # CTR (0-1)
    impressions: int = 0  # インプレッション数
    
    # 時系列データ
    published_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    peak_traffic_date: Optional[datetime] = None
    
    # エンゲージメント指標
    scroll_depth: float = 0.0  # スクロール深度 (0-1)
    return_visitor_rate: float = 0.0  # リピート率 (0-1)
    page_completion_rate: float = 0.0  # ページ完読率 (0-1)
    
    # カスタムタグ
    custom_tags: Dict[str, Any] = field(default_factory=dict)
    
    # 計算されるメトリクス
    @property
    def engagement_score(self) -> float:
        """エンゲージメントスコア計算"""
        score = (
            (1 - self.bounce_rate) * 0.3 +
            min(self.average_time_on_page / 300, 1.0) * 0.3 +  # 5分を上限
            self.scroll_depth * 0.2 +
            self.page_completion_rate * 0.2
        )
        return min(score, 1.0)
    
    @property
    def seo_performance_score(self) -> float:
        """SEOパフォーマンススコア計算"""
        position_score = max(0, (21 - self.average_search_position) / 20) if self.average_search_position > 0 else 0
        ctr_score = self.click_through_rate
        organic_score = self.organic_traffic_rate
        
        score = (position_score * 0.4 + ctr_score * 0.3 + organic_score * 0.3)
        return min(score, 1.0)
    
    @property
    def content_quality_score(self) -> float:
        """コンテンツ品質スコア計算"""
        # 文字数スコア（1500-3000文字が理想）
        word_score = min(1.0, max(0, self.word_count - 500) / 2500)
        
        # 構造スコア
        structure_score = min(1.0, (self.h2_count + self.h3_count) / 5)
        
        # 可読性スコア
        readability_normalized = self.readability_score / 100
        
        score = (word_score * 0.3 + structure_score * 0.2 + readability_normalized * 0.5)
        return min(score, 1.0)
    
    def add_custom_tag(self, tag_name: str, tag_value: Any) -> None:
        """カスタムタグの追加"""
        self.custom_tags[tag_name] = tag_value
        logger.info(f"Added custom tag {tag_name}: {tag_value} to article {self.article_id}")
    
    def remove_custom_tag(self, tag_name: str) -> bool:
        """カスタムタグの削除"""
        if tag_name in self.custom_tags:
            del self.custom_tags[tag_name]
            logger.info(f"Removed custom tag {tag_name} from article {self.article_id}")
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'article_id': self.article_id,
            'title': self.title,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'paragraph_count': self.paragraph_count,
            
            # SEO関連
            'primary_keyword': self.primary_keyword,
            'keyword_density': self.keyword_density,
            'seo_keywords': self.seo_keywords,
            'keyword_volumes': self.keyword_volumes,
            'semantic_keywords': self.semantic_keywords,
            'long_tail_keywords': self.long_tail_keywords,
            
            # 構造
            'h1_count': self.h1_count,
            'h2_count': self.h2_count,
            'h3_count': self.h3_count,
            'image_count': self.image_count,
            'internal_link_count': self.internal_link_count,
            'external_link_count': self.external_link_count,
            'list_count': self.list_count,
            'table_count': self.table_count,
            
            # トンマナ
            'tone_style': self.tone_style.value,
            'writing_formality': self.writing_formality.value,
            'target_audience': self.target_audience.value,
            'emotional_tone': self.emotional_tone.value,
            
            # 可読性
            'readability_score': self.readability_score,
            'average_sentence_length': self.average_sentence_length,
            'complex_word_ratio': self.complex_word_ratio,
            
            # パフォーマンス
            'page_views': self.page_views,
            'unique_visitors': self.unique_visitors,
            'average_time_on_page': self.average_time_on_page,
            'bounce_rate': self.bounce_rate,
            'conversion_rate': self.conversion_rate,
            'organic_traffic_rate': self.organic_traffic_rate,
            'social_shares': self.social_shares,
            'backlink_count': self.backlink_count,
            
            # 検索関連
            'average_search_position': self.average_search_position,
            'click_through_rate': self.click_through_rate,
            'impressions': self.impressions,
            
            # 時系列
            'published_date': self.published_date.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'peak_traffic_date': self.peak_traffic_date.isoformat() if self.peak_traffic_date else None,
            
            # エンゲージメント
            'scroll_depth': self.scroll_depth,
            'return_visitor_rate': self.return_visitor_rate,
            'page_completion_rate': self.page_completion_rate,
            
            # 計算されるスコア
            'engagement_score': self.engagement_score,
            'seo_performance_score': self.seo_performance_score,
            'content_quality_score': self.content_quality_score,
            
            # カスタム
            'custom_tags': self.custom_tags
        }


class ArticleMetricsManager:
    """記事メトリクス管理クラス"""
    
    def __init__(self):
        self.metrics_cache: Dict[int, ArticleMetrics] = {}
        logger.info("ArticleMetricsManager initialized")
    
    def add_metrics(self, metrics: ArticleMetrics) -> None:
        """メトリクスの追加"""
        self.metrics_cache[metrics.article_id] = metrics
        logger.info(f"Added metrics for article {metrics.article_id}")
    
    def get_metrics(self, article_id: int) -> Optional[ArticleMetrics]:
        """メトリクスの取得"""
        return self.metrics_cache.get(article_id)
    
    def update_performance_data(self, article_id: int, performance_data: Dict[str, Any]) -> bool:
        """パフォーマンスデータの更新"""
        if article_id not in self.metrics_cache:
            logger.warning(f"Article {article_id} not found in cache")
            return False
        
        metrics = self.metrics_cache[article_id]
        
        # パフォーマンス指標の更新
        for key, value in performance_data.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
        
        metrics.last_updated = datetime.now()
        logger.info(f"Updated performance data for article {article_id}")
        return True
    
    def bulk_update_tags(self, article_ids: List[int], tags: Dict[str, Any]) -> int:
        """一括タグ更新"""
        updated_count = 0
        
        for article_id in article_ids:
            if article_id in self.metrics_cache:
                metrics = self.metrics_cache[article_id]
                for tag_name, tag_value in tags.items():
                    metrics.add_custom_tag(tag_name, tag_value)
                updated_count += 1
        
        logger.info(f"Bulk updated tags for {updated_count} articles")
        return updated_count
    
    def get_all_metrics(self) -> List[ArticleMetrics]:
        """全メトリクスの取得"""
        return list(self.metrics_cache.values())
    
    def filter_by_tag(self, tag_name: str, tag_value: Any = None) -> List[ArticleMetrics]:
        """タグによるフィルタリング"""
        filtered = []
        
        for metrics in self.metrics_cache.values():
            if tag_name in metrics.custom_tags:
                if tag_value is None or metrics.custom_tags[tag_name] == tag_value:
                    filtered.append(metrics)
        
        return filtered
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンス要約統計"""
        if not self.metrics_cache:
            return {}
        
        all_metrics = list(self.metrics_cache.values())
        
        return {
            'total_articles': len(all_metrics),
            'average_conversion_rate': sum(m.conversion_rate for m in all_metrics) / len(all_metrics),
            'average_bounce_rate': sum(m.bounce_rate for m in all_metrics) / len(all_metrics),
            'average_engagement_score': sum(m.engagement_score for m in all_metrics) / len(all_metrics),
            'average_seo_score': sum(m.seo_performance_score for m in all_metrics) / len(all_metrics),
            'total_page_views': sum(m.page_views for m in all_metrics),
            'total_social_shares': sum(m.social_shares for m in all_metrics)
        }


if __name__ == "__main__":
    # テスト実行
    metrics = ArticleMetrics(
        article_id=1,
        title="1月の誕生花「水仙」完全ガイド",
        word_count=2500,
        character_count=3750,
        paragraph_count=12,
        primary_keyword="1月 誕生花",
        keyword_density=0.024,
        seo_keywords=["水仙", "花言葉", "育て方"],
        h2_count=5,
        h3_count=3,
        tone_style=ToneStyle.FRIENDLY,
        conversion_rate=0.045,
        bounce_rate=0.35,
        average_time_on_page=180.0
    )
    
    print(f"Engagement Score: {metrics.engagement_score:.3f}")
    print(f"SEO Performance Score: {metrics.seo_performance_score:.3f}")
    print(f"Content Quality Score: {metrics.content_quality_score:.3f}")
    
    # カスタムタグ追加
    metrics.add_custom_tag("campaign", "spring_flowers_2024")
    metrics.add_custom_tag("author", "expert_writer")
    
    print(f"Custom tags: {metrics.custom_tags}")