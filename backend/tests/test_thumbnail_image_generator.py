"""
Test for Thumbnail Image Generator  
サムネイル画像生成機能のテスト
TDD Red Phase: テスト作成
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
import base64
import io
from PIL import Image


@pytest.fixture
def sample_birth_flower_context():
    """誕生花記事コンテキスト"""
    return {
        "month": 3,
        "flower_name": "チューリップ",
        "flower_colors": ["赤", "白", "黄色", "ピンク"],
        "article_title": "3月の誕生花チューリップの花言葉と魅力を徹底解説",
        "primary_keyword": "3月 誕生花",
        "mood": "明るく優しい",
        "target_emotion": "春の喜び、新しい始まり",
        "style_preference": "自然で美しい",
        "season": "春"
    }


@pytest.fixture
def image_generation_requirements():
    """画像生成要件"""
    return {
        "dimensions": {"width": 1200, "height": 630},  # OGP推奨サイズ
        "format": "JPEG",
        "quality": 85,
        "max_file_size": 1024 * 1024,  # 1MB
        "supported_providers": ["gemini", "dalle3", "stable_diffusion"],
        "fallback_enabled": True
    }


@pytest.fixture
def mock_image_data():
    """モック画像データ"""
    # 小さなテスト用画像を生成
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    return base64.b64encode(img_byte_arr).decode('utf-8')


class TestThumbnailImageGenerator:
    """サムネイル画像生成器のテストクラス"""

    def test_generate_thumbnail_image_基本機能(self, sample_birth_flower_context):
        """基本的なサムネイル画像生成機能のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        result = generator.generate_thumbnail_image(sample_birth_flower_context)
        
        assert result is not None
        assert "image_data" in result
        assert "metadata" in result
        assert "generation_info" in result
        
        metadata = result["metadata"]
        assert metadata["width"] == 1200
        assert metadata["height"] == 630
        assert metadata["format"] == "JPEG"

    @pytest.mark.asyncio
    async def test_gemini_image_generation_Gemini生成(self, sample_birth_flower_context, mock_image_data):
        """Gemini APIによる画像生成テスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        with patch('src.content.thumbnail_image_generator.ThumbnailImageGenerator._call_gemini_api') as mock_gemini:
            mock_gemini.return_value = {
                "image_data": mock_image_data,
                "prompt": "Beautiful spring tulips in a garden",
                "generation_time": 5.2
            }
            
            result = await generator.generate_with_gemini(sample_birth_flower_context)
            
            assert result is not None
            assert "image_data" in result
            assert "prompt" in result
            assert "チューリップ" in result.get("prompt", "")
            mock_gemini.assert_called_once()

    @pytest.mark.asyncio  
    async def test_dalle3_image_generation_DALLE3生成(self, sample_birth_flower_context, mock_image_data):
        """DALL-E 3による画像生成テスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        with patch('src.content.thumbnail_image_generator.ThumbnailImageGenerator._call_dalle3_api') as mock_dalle:
            mock_dalle.return_value = {
                "image_url": "https://example.com/generated_image.jpg",
                "image_data": mock_image_data,
                "revised_prompt": "A beautiful arrangement of colorful tulips",
                "generation_time": 8.1
            }
            
            result = await generator.generate_with_dalle3(sample_birth_flower_context)
            
            assert result is not None
            assert "image_data" in result
            assert "revised_prompt" in result
            mock_dalle.assert_called_once()

    @pytest.mark.asyncio
    async def test_stable_diffusion_generation_StableDiffusion生成(self, sample_birth_flower_context, mock_image_data):
        """Stable Diffusionによる画像生成テスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        with patch('src.content.thumbnail_image_generator.ThumbnailImageGenerator._call_stable_diffusion_api') as mock_sd:
            mock_sd.return_value = {
                "image_data": mock_image_data,
                "seed": 12345,
                "steps": 20,
                "generation_time": 12.5
            }
            
            result = await generator.generate_with_stable_diffusion(sample_birth_flower_context)
            
            assert result is not None
            assert "image_data" in result
            assert "seed" in result
            mock_sd.assert_called_once()

    def test_prompt_template_management_プロンプト管理(self, sample_birth_flower_context):
        """プロンプトテンプレート管理機能のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 基本プロンプト生成
        prompt = generator.generate_prompt(sample_birth_flower_context)
        assert isinstance(prompt, str)
        assert "チューリップ" in prompt
        assert "3月" in prompt or "春" in prompt
        
        # テンプレート別プロンプト生成
        realistic_prompt = generator.generate_prompt(sample_birth_flower_context, style="realistic")
        artistic_prompt = generator.generate_prompt(sample_birth_flower_context, style="artistic")
        minimalist_prompt = generator.generate_prompt(sample_birth_flower_context, style="minimalist")
        
        assert realistic_prompt != artistic_prompt
        assert artistic_prompt != minimalist_prompt
        assert all("チューリップ" in p for p in [realistic_prompt, artistic_prompt, minimalist_prompt])

    def test_birth_flower_specific_templates_誕生花特化テンプレート(self, sample_birth_flower_context):
        """誕生花特化プロンプトテンプレートのテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 月別特化プロンプト
        march_prompt = generator.generate_month_specific_prompt(sample_birth_flower_context)
        assert "春" in march_prompt or "3月" in march_prompt
        assert "チューリップ" in march_prompt
        
        # 花言葉統合プロンプト
        flower_language_prompt = generator.generate_flower_language_prompt(sample_birth_flower_context)
        assert "花言葉" in flower_language_prompt or "意味" in flower_language_prompt
        
        # ギフト文脈プロンプト
        gift_context_prompt = generator.generate_gift_context_prompt(sample_birth_flower_context)
        assert any(word in gift_context_prompt for word in ["プレゼント", "ギフト", "贈り物"])

    @pytest.mark.asyncio
    async def test_multi_provider_fallback_複数プロバイダー対応(self, sample_birth_flower_context, mock_image_data):
        """複数プロバイダーによるフォールバック機能のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 最初のプロバイダーが失敗した場合のフォールバック
        with patch('src.content.thumbnail_image_generator.ThumbnailImageGenerator._call_gemini_api') as mock_gemini, \
             patch('src.content.thumbnail_image_generator.ThumbnailImageGenerator._call_dalle3_api') as mock_dalle:
            
            mock_gemini.side_effect = Exception("Gemini API error")
            mock_dalle.return_value = {
                "image_data": mock_image_data,
                "revised_prompt": "Fallback generation successful"
            }
            
            result = await generator.generate_with_fallback(sample_birth_flower_context, 
                                                          providers=["gemini", "dalle3"])
            
            assert result is not None
            assert "image_data" in result
            assert result.get("used_provider") == "dalle3"
            mock_gemini.assert_called_once()
            mock_dalle.assert_called_once()

    def test_image_optimization_画像最適化(self, sample_birth_flower_context, mock_image_data):
        """画像最適化機能のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 画像リサイズとフォーマット最適化
        optimized_result = generator.optimize_image(
            mock_image_data, 
            target_size=(1200, 630),
            format="JPEG",
            quality=85
        )
        
        assert "optimized_image_data" in optimized_result
        assert "file_size" in optimized_result
        assert "dimensions" in optimized_result
        assert optimized_result["file_size"] <= 1024 * 1024  # 1MB以下

    def test_batch_generation_一括生成(self, sample_birth_flower_context):
        """複数バリエーション一括生成のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 複数スタイルでの一括生成
        batch_result = generator.generate_multiple_variations(
            sample_birth_flower_context,
            styles=["realistic", "artistic", "minimalist"],
            count=3
        )
        
        assert len(batch_result) == 3
        assert all("image_data" in result for result in batch_result)
        assert all("style" in result for result in batch_result)
        
        # 異なるスタイルが適用されていることを確認
        styles_used = [result["style"] for result in batch_result]
        assert len(set(styles_used)) == 3

    def test_metadata_extraction_メタデータ抽出(self, sample_birth_flower_context, mock_image_data):
        """生成画像からのメタデータ抽出テスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        metadata = generator.extract_image_metadata(mock_image_data)
        
        assert "width" in metadata
        assert "height" in metadata
        assert "format" in metadata
        assert "file_size" in metadata
        assert "color_profile" in metadata

    def test_prompt_validation_プロンプト検証(self, sample_birth_flower_context):
        """プロンプト検証機能のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 有効なプロンプトの検証
        valid_prompt = generator.generate_prompt(sample_birth_flower_context)
        validation_result = generator.validate_prompt(valid_prompt)
        
        assert validation_result["is_valid"] is True
        assert validation_result["quality_score"] > 0
        assert "suggestions" in validation_result

    def test_cost_optimization_コスト最適化(self, sample_birth_flower_context):
        """コスト最適化機能のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # コスト効率の良いプロバイダー選択
        cost_analysis = generator.analyze_generation_cost(
            sample_birth_flower_context,
            providers=["gemini", "dalle3", "stable_diffusion"]
        )
        
        assert "recommended_provider" in cost_analysis
        assert "cost_comparison" in cost_analysis
        assert "quality_vs_cost_ratio" in cost_analysis

    def test_seasonal_enhancement_季節強化(self, sample_birth_flower_context):
        """季節感強化機能のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 春の季節感を強化したプロンプト
        enhanced_prompt = generator.enhance_seasonal_elements(sample_birth_flower_context)
        
        spring_keywords = ["春", "桜", "新芽", "暖かい", "明るい", "爽やか"]
        found_keywords = [kw for kw in spring_keywords if kw in enhanced_prompt]
        assert len(found_keywords) >= 2, f"季節感キーワードが不足: {enhanced_prompt}"

    def test_error_handling_エラーハンドリング(self, sample_birth_flower_context):
        """エラーハンドリングのテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 空の入力に対するエラーハンドリング
        with pytest.raises(ValueError, match="Birth flower context is required"):
            generator.generate_thumbnail_image({})
        
        # 不正な花名に対するエラーハンドリング
        invalid_context = sample_birth_flower_context.copy()
        invalid_context["flower_name"] = ""
        
        with pytest.raises(ValueError, match="Flower name is required"):
            generator.generate_thumbnail_image(invalid_context)

    @pytest.mark.asyncio
    async def test_performance_benchmarks_パフォーマンス(self, sample_birth_flower_context):
        """パフォーマンステスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        import time
        
        generator = ThumbnailImageGenerator()
        
        # プロンプト生成のパフォーマンス
        start_time = time.time()
        prompt = generator.generate_prompt(sample_birth_flower_context)
        end_time = time.time()
        
        prompt_generation_time = end_time - start_time
        assert prompt_generation_time < 1.0, f"プロンプト生成時間が遅すぎます: {prompt_generation_time}秒"

    def test_accessibility_considerations_アクセシビリティ(self, sample_birth_flower_context):
        """アクセシビリティ配慮のテスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # ALTテキスト生成
        alt_text = generator.generate_alt_text(sample_birth_flower_context)
        assert isinstance(alt_text, str)
        assert len(alt_text) > 10
        assert "チューリップ" in alt_text
        
        # カラーコントラストの考慮
        accessibility_check = generator.check_accessibility_compliance(sample_birth_flower_context)
        assert "color_contrast" in accessibility_check
        assert "alt_text_quality" in accessibility_check

    def test_integration_with_article_context_記事統合(self, sample_birth_flower_context):
        """記事コンテキストとの統合テスト"""
        from src.content.thumbnail_image_generator import ThumbnailImageGenerator
        
        generator = ThumbnailImageGenerator()
        
        # 記事タイトルとの整合性チェック
        consistency_check = generator.validate_article_consistency(sample_birth_flower_context)
        assert consistency_check["title_alignment"] is True
        assert consistency_check["keyword_alignment"] is True
        assert "consistency_score" in consistency_check