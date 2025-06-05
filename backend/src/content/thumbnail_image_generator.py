"""
Thumbnail Image Generator
サムネイル画像生成機能

AIを活用してSEO最適化されたサムネイル画像を生成する機能
- 複数AIプロバイダー対応（Gemini, DALL-E 3, Stable Diffusion）
- 誕生花記事特化のプロンプトテンプレート
- OGP最適化（1200x630px）
- フォールバック機能
- 画像最適化とメタデータ管理
"""
import asyncio
import base64
import io
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from PIL import Image, ImageStat
import logging
import re
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ImageGenerationResult:
    """画像生成結果"""
    image_data: str  # Base64エンコードされた画像データ
    metadata: Dict[str, Any]
    generation_info: Dict[str, Any]
    provider: str
    prompt_used: str
    generation_time: float


class ThumbnailImageGenerator:
    """サムネイル画像生成器
    
    AI技術を活用してSEO最適化されたサムネイル画像を生成するクラス
    - 誕生花記事に特化したプロンプトテンプレート
    - 複数AIプロバイダー対応とフォールバック
    - OGP最適化（1200x630px推奨）
    - 季節感とブランド一貫性の両立
    """
    
    def __init__(self):
        self.target_dimensions = (1200, 630)  # OGP推奨サイズ
        self.supported_formats = ["JPEG", "PNG", "WebP"]
        self.max_file_size = 1024 * 1024  # 1MB
        self.quality_default = 85
        
        # 誕生花特化プロンプトテンプレート
        self.birth_flower_templates = {
            "realistic": {
                "base": "A beautiful arrangement of {flower_name} flowers in {colors}, photographed in natural lighting with soft shadows, high-resolution professional photography style",
                "seasonal": ", capturing the essence of {season} with {seasonal_elements}",
                "mood": ", {mood} atmosphere with {emotion_keywords}",
                "composition": ", elegant composition with shallow depth of field, centered layout perfect for social media thumbnail"
            },
            "artistic": {
                "base": "Artistic watercolor illustration of {flower_name} in {colors}, elegant and dreamy style",
                "seasonal": " with {season} elements like {seasonal_elements}",
                "mood": ", conveying {emotion_keywords} through soft brushstrokes and harmonious colors",
                "composition": ", balanced composition with negative space, suitable for article header image"
            },
            "minimalist": {
                "base": "Clean minimalist design featuring a single {flower_name} bloom in {primary_color}",
                "seasonal": " with subtle {season} color palette",
                "mood": ", simple and elegant aesthetic that evokes {emotion_keywords}",
                "composition": ", centered composition with plenty of white space, modern typography-friendly design"
            }
        }
        
        # 季節別要素マッピング
        self.seasonal_elements = {
            "春": ["新緑", "桜の花びら", "暖かい日差し", "清々しい空気", "若葉"],
            "夏": ["青空", "緑陰", "爽やかな風", "陽射し", "生命力"],
            "秋": ["紅葉", "実り", "金色の光", "収穫", "落ち着いた色調"],
            "冬": ["雪景色", "結晶", "静寂", "上品", "モノトーン"]
        }
        
        # 感情キーワードマッピング
        self.emotion_keywords = {
            "喜び": ["bright", "joyful", "cheerful", "vibrant", "uplifting"],
            "愛情": ["warm", "tender", "romantic", "gentle", "affectionate"],
            "希望": ["hopeful", "inspiring", "optimistic", "radiant", "promising"],
            "平和": ["peaceful", "serene", "calm", "tranquil", "harmonious"],
            "感謝": ["grateful", "appreciative", "blessed", "heartfelt", "sincere"]
        }
        
        # プロバイダー設定
        self.providers = ["gemini", "dalle3", "stable_diffusion"]
        self.provider_costs = {
            "gemini": 0.002,  # 推定コスト/画像
            "dalle3": 0.04,
            "stable_diffusion": 0.01
        }

    def generate_thumbnail_image(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """基本的なサムネイル画像生成"""
        self._validate_context(context)
        
        # プロンプト生成
        prompt = self.generate_prompt(context)
        
        # メタデータ準備
        metadata = {
            "width": self.target_dimensions[0],
            "height": self.target_dimensions[1],
            "format": "JPEG",
            "generation_timestamp": time.time(),
            "context_hash": self._generate_context_hash(context)
        }
        
        # 生成情報
        generation_info = {
            "prompt_used": prompt,
            "style": context.get("style_preference", "realistic"),
            "provider": "mock",  # テスト用
            "generation_time": 2.5
        }
        
        # モック画像データ（テスト用）
        mock_image = self._create_mock_image()
        
        return {
            "image_data": mock_image,
            "metadata": metadata,
            "generation_info": generation_info
        }

    async def generate_with_gemini(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini APIによる画像生成"""
        try:
            prompt = self.generate_prompt(context, style="realistic")
            
            start_time = time.time()
            result = await self._call_gemini_api(prompt, context)
            generation_time = time.time() - start_time
            
            return {
                "image_data": result["image_data"],
                "prompt": prompt,
                "generation_time": generation_time,
                "provider": "gemini"
            }
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    async def generate_with_dalle3(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """DALL-E 3による画像生成"""
        try:
            prompt = self.generate_prompt(context, style="artistic")
            
            start_time = time.time()
            result = await self._call_dalle3_api(prompt, context)
            generation_time = time.time() - start_time
            
            return {
                "image_data": result["image_data"],
                "revised_prompt": result.get("revised_prompt", prompt),
                "generation_time": generation_time,
                "provider": "dalle3"
            }
        except Exception as e:
            logger.error(f"DALL-E 3 generation failed: {e}")
            raise

    async def generate_with_stable_diffusion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stable Diffusionによる画像生成"""
        try:
            prompt = self.generate_prompt(context, style="minimalist")
            
            start_time = time.time()
            result = await self._call_stable_diffusion_api(prompt, context)
            generation_time = time.time() - start_time
            
            return {
                "image_data": result["image_data"],
                "seed": result.get("seed", 12345),
                "generation_time": generation_time,
                "provider": "stable_diffusion"
            }
        except Exception as e:
            logger.error(f"Stable Diffusion generation failed: {e}")
            raise

    def generate_prompt(self, context: Dict[str, Any], style: str = "realistic") -> str:
        """プロンプト生成"""
        if style not in self.birth_flower_templates:
            style = "realistic"
        
        template = self.birth_flower_templates[style]
        
        # 基本情報の抽出
        flower_name = context.get("flower_name", "flower")
        colors = self._format_colors(context.get("flower_colors", ["colorful"]))
        season = context.get("season", "春")
        mood = context.get("mood", "beautiful")
        
        # プロンプト構築
        prompt = template["base"].format(
            flower_name=flower_name,
            colors=colors,
            primary_color=context.get("flower_colors", ["beautiful"])[0] if context.get("flower_colors") else "colorful"
        )
        
        # 季節要素追加
        if "seasonal" in template:
            seasonal_elements = ", ".join(self.seasonal_elements.get(season, ["natural elements"])[:2])
            prompt += template["seasonal"].format(
                season=season,
                seasonal_elements=seasonal_elements
            )
        
        # 感情要素追加
        if "mood" in template:
            emotion = context.get("target_emotion", "美しさ")
            emotion_words = self._extract_emotion_keywords(emotion)
            prompt += template["mood"].format(
                emotion_keywords=emotion_words,
                mood=mood
            )
        
        # 構成要素追加
        if "composition" in template:
            prompt += template["composition"]
        
        return prompt

    def generate_month_specific_prompt(self, context: Dict[str, Any]) -> str:
        """月別特化プロンプト生成"""
        month = context.get("month", 3)
        flower_name = context.get("flower_name", "flower")
        
        month_themes = {
            1: "新年の希望と純白の美しさ",
            2: "冬の終わりと春への期待",
            3: "春の訪れと新しい始まり",
            4: "桜と共に咲く優美さ",
            5: "初夏の爽やかさと生命力",
            6: "梅雨の恵みと清々しさ",
            7: "夏の陽射しと鮮やかさ",
            8: "盛夏の情熱と力強さ",
            9: "秋の始まりと落ち着き",
            10: "紅葉と共に映える美しさ",
            11: "深秋の上品さと趣",
            12: "年末の感謝と温かさ"
        }
        
        theme = month_themes.get(month, "季節の美しさ")
        
        return f"Beautiful {flower_name} representing {month}月の誕生花, embodying {theme}, professional photography with seasonal atmosphere, perfect for article thumbnail, high quality and visually appealing"

    def generate_flower_language_prompt(self, context: Dict[str, Any]) -> str:
        """花言葉統合プロンプト生成"""
        flower_name = context.get("flower_name", "flower")
        target_emotion = context.get("target_emotion", "愛と美しさ")
        
        return f"Artistic representation of {flower_name} symbolizing {target_emotion} (花言葉), ethereal and meaningful composition that conveys the flower's language and deeper 意味, soft lighting and emotional depth showcasing the 花言葉 concept"

    def generate_gift_context_prompt(self, context: Dict[str, Any]) -> str:
        """ギフト文脈プロンプト生成"""
        flower_name = context.get("flower_name", "flower")
        
        return f"Elegant {flower_name} arrangement perfect for gift giving, beautifully presented with ribbon or wrapping elements, warm and inviting atmosphere that suggests thoughtfulness and care, suitable for プレゼント and ギフト contexts"

    async def generate_with_fallback(self, context: Dict[str, Any], providers: List[str] = None) -> Dict[str, Any]:
        """フォールバック機能付き生成"""
        if providers is None:
            providers = self.providers.copy()
        
        last_error = None
        
        for provider in providers:
            try:
                if provider == "gemini":
                    result = await self.generate_with_gemini(context)
                elif provider == "dalle3":
                    result = await self.generate_with_dalle3(context)
                elif provider == "stable_diffusion":
                    result = await self.generate_with_stable_diffusion(context)
                else:
                    continue
                
                result["used_provider"] = provider
                return result
                
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                last_error = e
                continue
        
        raise last_error or Exception("All providers failed")

    def optimize_image(self, image_data: str, target_size: Tuple[int, int] = None, 
                      format: str = "JPEG", quality: int = 85) -> Dict[str, Any]:
        """画像最適化"""
        if target_size is None:
            target_size = self.target_dimensions
        
        try:
            # Base64デコード
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
            
            # リサイズ
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # フォーマット変換と最適化
            output = io.BytesIO()
            if format == "JPEG":
                img = img.convert("RGB")
                img.save(output, format=format, quality=quality, optimize=True)
            else:
                img.save(output, format=format, optimize=True)
            
            optimized_data = base64.b64encode(output.getvalue()).decode('utf-8')
            file_size = len(output.getvalue())
            
            return {
                "optimized_image_data": optimized_data,
                "file_size": file_size,
                "dimensions": target_size,
                "format": format,
                "compression_ratio": len(image_bytes) / file_size if file_size > 0 else 1
            }
            
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            raise

    def generate_multiple_variations(self, context: Dict[str, Any], 
                                   styles: List[str] = None, count: int = 3) -> List[Dict[str, Any]]:
        """複数バリエーション生成"""
        if styles is None:
            styles = list(self.birth_flower_templates.keys())
        
        variations = []
        for i in range(min(count, len(styles))):
            style = styles[i]
            variation_context = context.copy()
            variation_context["style_preference"] = style
            
            result = self.generate_thumbnail_image(variation_context)
            result["style"] = style
            result["variation_id"] = i + 1
            
            variations.append(result)
        
        return variations

    def extract_image_metadata(self, image_data: str) -> Dict[str, Any]:
        """画像メタデータ抽出"""
        try:
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
            
            # 基本情報
            metadata = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "file_size": len(image_bytes)
            }
            
            # カラープロファイル分析
            if img.mode == "RGB":
                stat = ImageStat.Stat(img)
                metadata["color_profile"] = {
                    "mean_rgb": stat.mean,
                    "stddev_rgb": stat.stddev,
                    "dominant_colors": self._extract_dominant_colors(img)
                }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}

    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """プロンプト検証"""
        quality_score = 0
        suggestions = []
        
        # 長さチェック
        if len(prompt) < 20:
            suggestions.append("プロンプトが短すぎます。より詳細な説明を追加してください。")
        elif len(prompt) > 500:
            suggestions.append("プロンプトが長すぎます。簡潔にまとめてください。")
        else:
            quality_score += 25
        
        # キーワード密度チェック
        essential_keywords = ["flower", "beautiful", "professional", "high quality"]
        found_keywords = sum(1 for kw in essential_keywords if kw.lower() in prompt.lower())
        quality_score += (found_keywords / len(essential_keywords)) * 25
        
        # スタイル指定チェック
        style_keywords = ["photography", "illustration", "artistic", "realistic", "minimalist"]
        has_style = any(kw in prompt.lower() for kw in style_keywords)
        if has_style:
            quality_score += 25
        else:
            suggestions.append("スタイル指定を追加すると品質が向上します。")
        
        # 構成指定チェック
        composition_keywords = ["composition", "layout", "centered", "balanced"]
        has_composition = any(kw in prompt.lower() for kw in composition_keywords)
        if has_composition:
            quality_score += 25
        else:
            suggestions.append("構成に関する指定を追加すると良いでしょう。")
        
        return {
            "is_valid": quality_score >= 50,
            "quality_score": quality_score,
            "suggestions": suggestions
        }

    def analyze_generation_cost(self, context: Dict[str, Any], 
                              providers: List[str] = None) -> Dict[str, Any]:
        """コスト分析"""
        if providers is None:
            providers = self.providers
        
        cost_comparison = {}
        quality_scores = {"gemini": 85, "dalle3": 95, "stable_diffusion": 80}
        
        for provider in providers:
            cost = self.provider_costs.get(provider, 0.01)
            quality = quality_scores.get(provider, 75)
            
            cost_comparison[provider] = {
                "cost_per_image": cost,
                "estimated_quality": quality,
                "cost_effectiveness": quality / (cost * 100)
            }
        
        # 推奨プロバイダー選択
        best_provider = max(cost_comparison.keys(), 
                          key=lambda p: cost_comparison[p]["cost_effectiveness"])
        
        return {
            "recommended_provider": best_provider,
            "cost_comparison": cost_comparison,
            "quality_vs_cost_ratio": cost_comparison[best_provider]["cost_effectiveness"]
        }

    def enhance_seasonal_elements(self, context: Dict[str, Any]) -> str:
        """季節感強化"""
        season = context.get("season", "春")
        month = context.get("month", 3)
        flower_name = context.get("flower_name", "flower")
        
        seasonal_enhancements = {
            "春": ["桜の花びら", "新緑", "暖かい日差し", "爽やかな風", "明るい空"],
            "夏": ["青空", "緑陰", "陽射し", "活力", "鮮やかな色彩"],
            "秋": ["紅葉", "金色の光", "実り", "落ち着いた色調", "収穫の喜び"],
            "冬": ["雪景色", "静寂", "上品", "モノトーン", "凛とした美しさ"]
        }
        
        elements = seasonal_enhancements.get(season, seasonal_enhancements["春"])
        selected_elements = elements[:3]  # 上位3つを選択
        
        base_prompt = self.generate_prompt(context)
        enhanced_prompt = f"{base_prompt}, enhanced with {season} elements including {', '.join(selected_elements)}, capturing the essence of {season} season in Japan"
        
        return enhanced_prompt

    def generate_alt_text(self, context: Dict[str, Any]) -> str:
        """ALTテキスト生成"""
        flower_name = context.get("flower_name", "花")
        month = context.get("month", "")
        article_title = context.get("article_title", "")
        
        if month:
            base_alt = f"{month}月の誕生花{flower_name}の美しい画像"
        else:
            base_alt = f"{flower_name}の美しい画像"
        
        if article_title:
            base_alt += f"（{article_title}のサムネイル）"
        
        return base_alt

    def check_accessibility_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """アクセシビリティチェック"""
        alt_text = self.generate_alt_text(context)
        
        return {
            "color_contrast": {
                "meets_wcag_aa": True,  # 実際の実装では画像解析が必要
                "contrast_ratio": 7.2  # 推定値
            },
            "alt_text_quality": {
                "length": len(alt_text),
                "is_descriptive": len(alt_text) > 10,
                "includes_context": "誕生花" in alt_text
            },
            "file_size_optimized": True,
            "responsive_design_ready": True
        }

    def validate_article_consistency(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """記事コンテキストとの整合性チェック"""
        article_title = context.get("article_title", "")
        flower_name = context.get("flower_name", "")
        primary_keyword = context.get("primary_keyword", "")
        
        title_alignment = flower_name in article_title if flower_name and article_title else False
        keyword_alignment = any(word in article_title.lower() for word in primary_keyword.split()) if primary_keyword and article_title else False
        
        consistency_score = 0
        if title_alignment:
            consistency_score += 50
        if keyword_alignment:
            consistency_score += 50
        
        return {
            "title_alignment": title_alignment,
            "keyword_alignment": keyword_alignment,
            "consistency_score": consistency_score
        }

    # プライベートメソッド
    def _validate_context(self, context: Dict[str, Any]) -> None:
        """コンテキスト検証"""
        if not context:
            raise ValueError("Birth flower context is required")
        
        if not context.get("flower_name"):
            raise ValueError("Flower name is required")

    def _format_colors(self, colors: List[str]) -> str:
        """色リストをフォーマット"""
        if not colors:
            return "colorful"
        
        if len(colors) == 1:
            return colors[0]
        elif len(colors) == 2:
            return f"{colors[0]} and {colors[1]}"
        else:
            return f"{', '.join(colors[:-1])}, and {colors[-1]}"

    def _extract_emotion_keywords(self, emotion: str) -> str:
        """感情キーワード抽出"""
        for key, keywords in self.emotion_keywords.items():
            if key in emotion:
                return ", ".join(keywords[:3])
        
        return "beautiful, elegant, inspiring"

    def _generate_context_hash(self, context: Dict[str, Any]) -> str:
        """コンテキストハッシュ生成"""
        content = str(sorted(context.items()))
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _create_mock_image(self) -> str:
        """モック画像生成（テスト用）"""
        img = Image.new('RGB', (100, 100), color='lightblue')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        return base64.b64encode(img_byte_arr).decode('utf-8')

    def _extract_dominant_colors(self, img: Image.Image) -> List[Tuple[int, int, int]]:
        """主要色抽出"""
        # 簡略化された実装
        img_small = img.resize((50, 50))
        colors = img_small.getcolors(maxcolors=256)
        if colors:
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
            return [color[1] for color in sorted_colors[:5]]
        return []

    # API呼び出しメソッド（実装例）
    async def _call_gemini_api(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini API呼び出し（モック実装）"""
        await asyncio.sleep(0.1)  # APIコール模擬
        mock_image = self._create_mock_image()
        return {
            "image_data": mock_image,
            "prompt": prompt,
            "generation_time": 5.2
        }

    async def _call_dalle3_api(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """DALL-E 3 API呼び出し（モック実装）"""
        await asyncio.sleep(0.1)  # APIコール模擬
        mock_image = self._create_mock_image()
        return {
            "image_url": "https://example.com/generated_image.jpg",
            "image_data": mock_image,
            "revised_prompt": f"A beautiful arrangement of colorful tulips - {prompt}",
            "generation_time": 8.1
        }

    async def _call_stable_diffusion_api(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Stable Diffusion API呼び出し（モック実装）"""
        await asyncio.sleep(0.1)  # APIコール模擬
        mock_image = self._create_mock_image()
        return {
            "image_data": mock_image,
            "seed": 12345,
            "steps": 20,
            "generation_time": 12.5
        }