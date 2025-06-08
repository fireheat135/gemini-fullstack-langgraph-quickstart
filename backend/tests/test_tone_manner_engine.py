"""
Test Suite for Tone & Manner Engine
トンマナ一貫性チェック機能のテスト

Test Coverage:
1. 過去記事とのトンマナ比較
2. 文体・表現一貫性チェック
3. ブランドボイス適合性評価
4. 修正提案生成
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio

from src.content.tone_manner_engine import (
    ToneMannerEngine,
    ToneMannerAnalysis,
    ConsistencyReport,
    BrandVoiceProfile,
    ToneRecommendation,
    WritingStyle,
    FormalityLevel,
    ToneType,
    InconsistencyType,
    RecommendationType
)

from src.content.content_management_system import (
    ArticleContent,
    ToneManner
)


class TestToneMannerEngine:
    
    @pytest.fixture
    def tone_engine(self):
        """Tone & Manner Engine instance for testing"""
        return ToneMannerEngine()
    
    @pytest.fixture
    def brand_voice_profile(self) -> BrandVoiceProfile:
        """テスト用ブランドボイスプロファイル"""
        return BrandVoiceProfile(
            brand_name="花の専門サイト",
            preferred_tone=ToneType.FRIENDLY,
            preferred_formality=FormalityLevel.CASUAL,
            preferred_writing_style=WritingStyle.INFORMATIVE,
            target_audience="花好きの女性（20-50代）",
            brand_keywords=["美しい", "癒し", "自然", "優雅", "心地よい"],
            avoid_keywords=["難しい", "複雑", "専門的すぎる"],
            voice_characteristics={
                "warmth": 0.8,
                "professionalism": 0.6,
                "friendliness": 0.9,
                "expertise": 0.7,
                "accessibility": 0.8
            },
            style_guidelines={
                "use_honorifics": False,
                "use_casual_expressions": True,
                "include_seasonal_references": True,
                "focus_on_emotions": True
            }
        )

    # ===== 基本機能のテスト =====
    
    def test_tone_engine_initialization(self, tone_engine):
        """Tone Manner Engine初期化テスト"""
        assert isinstance(tone_engine, ToneMannerEngine)
        assert hasattr(tone_engine, 'brand_voice_profile')
        assert hasattr(tone_engine, 'historical_articles')

    def test_analyze_tone_manner_basic(self, tone_engine):
        """基本的なトンマナ分析テスト"""
        test_article = ArticleContent(
            id="test_1",
            title="テスト記事",
            content="これはテスト記事です。親しみやすい文体で書かれています。",
            keyword="テスト",
            tone_manner=ToneManner(
                tone="親しみやすい",
                formality="カジュアル",
                target_audience="一般",
                writing_style="情報提供型"
            ),
            created_at=datetime.now()
        )
        
        analysis = tone_engine.analyze_tone_manner(test_article)
        
        assert isinstance(analysis, ToneMannerAnalysis)
        assert 0 <= analysis.consistency_score <= 1
        assert analysis.target_tone_match is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF < /dev/null