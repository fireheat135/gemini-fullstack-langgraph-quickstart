"""
AI Services related type definitions
AIサービス関連の型定義
"""
from typing import TypedDict, Literal, Optional, List, Dict, Any, Protocol
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

# Enums and Literal Types
AIProvider = Literal["gemini", "openai", "anthropic", "stability_ai"]
AIModelType = Literal["text_generation", "image_generation", "text_analysis", "code_generation"]
GenerationStatus = Literal["pending", "in_progress", "completed", "failed", "cancelled"]

# Input Types
class AIGenerationRequest(TypedDict):
    """AI生成リクエスト"""
    provider: AIProvider
    model_type: AIModelType
    prompt: str
    parameters: Dict[str, Any]
    max_tokens: Optional[int]
    temperature: Optional[float]
    user_id: str

class APIKeyConfiguration(TypedDict):
    """APIキー設定"""
    provider: AIProvider
    encrypted_key: str
    daily_limit: int
    monthly_limit: int
    cost_per_request: Decimal
    is_active: bool

# Result Types
@dataclass(frozen=True)
class AIGenerationResult:
    """AI生成結果"""
    request_id: str
    provider: AIProvider
    model_type: AIModelType
    status: GenerationStatus
    content: str
    metadata: Dict[str, Any]
    tokens_used: Optional[int]
    cost: Decimal
    generation_time_seconds: float
    created_at: datetime

@dataclass(frozen=True)
class APIUsageMetrics:
    """API使用メトリクス"""
    provider: AIProvider
    user_id: str
    requests_made: int
    tokens_consumed: int
    total_cost: Decimal
    average_response_time: float
    success_rate: float
    period_start: datetime
    period_end: datetime

@dataclass(frozen=True)
class ProviderCapabilities:
    """プロバイダー機能"""
    provider: AIProvider
    supported_models: List[str]
    max_tokens_per_request: int
    supports_streaming: bool
    supports_function_calling: bool
    rate_limits: Dict[str, int]
    pricing: Dict[str, Decimal]

# Protocol definitions for dependency injection
class AIProviderProtocol(Protocol):
    """AIプロバイダーインターフェース"""
    
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """テキスト生成"""
        ...
    
    async def generate_image(
        self, 
        prompt: str, 
        width: int = 1024, 
        height: int = 1024
    ) -> bytes:
        """画像生成"""
        ...
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """テキスト分析"""
        ...

class APIKeyManagerProtocol(Protocol):
    """APIキー管理インターフェース"""
    
    async def store_api_key(
        self, 
        user_id: str, 
        provider: AIProvider, 
        api_key: str
    ) -> bool:
        """APIキー保存"""
        ...
    
    async def get_api_key(
        self, 
        user_id: str, 
        provider: AIProvider
    ) -> Optional[str]:
        """APIキー取得"""
        ...
    
    async def validate_api_key(
        self, 
        provider: AIProvider, 
        api_key: str
    ) -> bool:
        """APIキー検証"""
        ...

# Error Types
@dataclass(frozen=True)
class AIServiceError:
    """AIサービスエラー"""
    provider: AIProvider
    error_code: str
    error_message: str
    retry_after: Optional[int]
    request_id: Optional[str]
    timestamp: datetime