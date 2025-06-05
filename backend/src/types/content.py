"""
Content-related type definitions
コンテンツ関連の型定義
"""
from typing import TypedDict, Literal, Optional, List, Dict, Any
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

# Enums and Literal Types
ContentType = Literal["article", "blog_post", "product_description", "landing_page"]
ContentStatus = Literal["draft", "in_review", "published", "archived"]
SEODifficulty = Literal["low", "medium", "high", "very_high"]

# Input Types (TypedDict for runtime validation)
class MetaDescriptionContext(TypedDict):
    """メタディスクリプション生成のコンテキスト"""
    title: str
    primary_keyword: str
    secondary_keywords: List[str]
    content_summary: str
    target_emotion: Optional[str]
    call_to_action: Optional[str]
    tone: Optional[str]

class ThumbnailImageContext(TypedDict):
    """サムネイル画像生成のコンテキスト"""
    month: int
    flower_name: str
    flower_colors: List[str]
    article_title: str
    primary_keyword: str
    mood: str
    target_emotion: str
    style_preference: str
    season: str

class KeywordAnalysisInput(TypedDict):
    """キーワード分析の入力"""
    primary_keyword: str
    target_location: Optional[str]
    language: str
    search_volume_threshold: Optional[int]

# Output/Result Types (dataclass for immutability and validation)
@dataclass(frozen=True)
class SEOScore:
    """SEOスコア"""
    total: Decimal
    keyword_optimization: Decimal
    content_quality: Decimal
    technical_seo: Decimal
    readability: Decimal

@dataclass(frozen=True)
class KeywordDensity:
    """キーワード密度"""
    keyword: str
    density: Decimal
    occurrences: int
    recommended_range: tuple[Decimal, Decimal]
    is_optimal: bool

@dataclass(frozen=True)
class MetaDescriptionResult:
    """メタディスクリプション生成結果"""
    text: str
    character_count: int
    seo_score: SEOScore
    keyword_analysis: List[KeywordDensity]
    recommendations: List[str]
    generated_at: datetime

@dataclass(frozen=True)
class ImageGenerationResult:
    """画像生成結果"""
    image_data: str  # Base64 encoded
    width: int
    height: int
    format: str
    file_size_bytes: int
    generation_provider: str
    prompt_used: str
    generation_time_seconds: float
    alt_text: str

@dataclass(frozen=True)
class KeywordAnalysisResult:
    """キーワード分析結果"""
    keyword: str
    search_volume: Optional[int]
    competition_level: SEODifficulty
    cpc: Optional[Decimal]
    related_keywords: List[str]
    seasonal_trends: Dict[str, float]
    opportunities: List[str]

# Complex Types for Business Logic
@dataclass(frozen=True)
class ContentQualityMetrics:
    """コンテンツ品質指標"""
    readability_score: Decimal
    seo_optimization_score: Decimal
    originality_score: Decimal
    fact_check_score: Decimal
    tone_consistency_score: Decimal
    overall_quality: Decimal

@dataclass(frozen=True)
class DuplicateContentResult:
    """重複コンテンツ検出結果"""
    similarity_percentage: Decimal
    duplicate_sections: List[str]
    source_urls: List[str]
    is_duplicate: bool
    recommendations: List[str]

# Database Entity Types
@dataclass
class ArticleEntity:
    """記事エンティティ"""
    id: str
    user_id: str
    title: str
    content: str
    content_type: ContentType
    status: ContentStatus
    meta_description: Optional[str]
    thumbnail_url: Optional[str]
    seo_score: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]