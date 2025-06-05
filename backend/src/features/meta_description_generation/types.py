"""
Type definitions for Meta Description Generation feature
メタディスクリプション生成機能の型定義
"""
from typing import TypedDict, Literal, Optional, List, Protocol
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ...types.content import MetaDescriptionContext, MetaDescriptionResult

# Feature-specific types
TemplateType = Literal["informational", "problem_solving", "comparative", "emotional"]
GenerationStrategy = Literal["template", "ai_enhanced", "hybrid"]

class MetaDescriptionGenerationRequest(TypedDict):
    """メタディスクリプション生成リクエスト"""
    context: MetaDescriptionContext
    strategy: GenerationStrategy
    template_type: Optional[TemplateType]
    max_variations: Optional[int]
    seo_requirements: Optional["SEORequirements"]

class SEORequirements(TypedDict):
    """SEO要件"""
    min_length: int
    max_length: int
    target_keyword_density: Decimal
    required_emotional_words: List[str]
    required_action_words: List[str]

@dataclass(frozen=True)
class GenerationTemplate:
    """生成テンプレート"""
    template_type: TemplateType
    base_pattern: str
    seasonal_pattern: Optional[str]
    mood_pattern: Optional[str]
    composition_pattern: Optional[str]
    variables: List[str]

@dataclass(frozen=True)
class KeywordAnalysis:
    """キーワード分析結果"""
    keyword: str
    density: Decimal
    occurrences: int
    is_optimal: bool
    recommendations: List[str]

@dataclass(frozen=True)
class LengthAnalysis:
    """長さ分析結果"""
    character_count: int
    within_limit: bool
    above_minimum: bool
    optimal_range: bool
    utilization_rate: Decimal

@dataclass(frozen=True)
class EmotionalAnalysis:
    """感情分析結果"""
    emotional_words_found: List[str]
    action_words_found: List[str]
    emotion_score: Decimal
    has_emotional_appeal: bool
    has_action_appeal: bool

@dataclass(frozen=True)
class SEOValidationResult:
    """SEO検証結果"""
    seo_score: Decimal
    keyword_analysis: List[KeywordAnalysis]
    length_analysis: LengthAnalysis
    emotional_analysis: EmotionalAnalysis
    recommendations: List[str]
    is_valid: bool

@dataclass(frozen=True)
class MetaDescriptionGenerationResult:
    """メタディスクリプション生成結果"""
    meta_description: str
    variations: List[str]
    seo_validation: SEOValidationResult
    generation_metadata: dict
    generated_at: datetime

# Protocol definitions
class MetaDescriptionGeneratorProtocol(Protocol):
    """メタディスクリプション生成器インターフェース"""
    
    def generate(
        self, 
        request: MetaDescriptionGenerationRequest
    ) -> MetaDescriptionGenerationResult:
        """メタディスクリプション生成"""
        ...
    
    def validate(
        self, 
        meta_description: str, 
        context: MetaDescriptionContext
    ) -> SEOValidationResult:
        """SEO検証"""
        ...

class TemplateManagerProtocol(Protocol):
    """テンプレート管理インターフェース"""
    
    def get_template(self, template_type: TemplateType) -> GenerationTemplate:
        """テンプレート取得"""
        ...
    
    def render_template(
        self, 
        template: GenerationTemplate, 
        context: MetaDescriptionContext
    ) -> str:
        """テンプレート描画"""
        ...

class KeywordAnalyzerProtocol(Protocol):
    """キーワード分析インターフェース"""
    
    def analyze_keywords(
        self, 
        text: str, 
        context: MetaDescriptionContext
    ) -> List[KeywordAnalysis]:
        """キーワード分析"""
        ...
    
    def calculate_density(self, text: str, keyword: str) -> Decimal:
        """キーワード密度計算"""
        ...