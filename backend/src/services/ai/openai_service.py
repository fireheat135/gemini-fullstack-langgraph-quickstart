"""OpenAI API service integration."""

import asyncio
from typing import Any, Dict, List, Optional

import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.models.api_key import APIKey


class OpenAIService:
    """Service for OpenAI API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service with API key."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
    
    @property
    def default_model(self) -> str:
        """Default OpenAI model to use."""
        return "gpt-4.5-preview"
    
    @property
    def available_models(self) -> List[str]:
        """List of available OpenAI models."""
        return [
            "gpt-4.5-preview",
            "gpt-4.1",
            "gpt-4o",
            "o3-mini",
            "gpt-4",
            "gpt-3.5-turbo",
        ]
    
    def configure_with_api_key(self, api_key_obj: APIKey) -> None:
        """Configure service with encrypted API key object."""
        from app.core.encryption import decrypt_api_key
        
        decrypted_key = decrypt_api_key(api_key_obj.encrypted_api_key)
        self.api_key = decrypted_key
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using OpenAI API."""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "OpenAI client not configured"
                }
            
            model_name = model_name or self.default_model
            
            # Prepare messages
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            # Generate content
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens or 4096,
                temperature=temperature or 0.7,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                **kwargs
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model_name,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_name or self.default_model,
            }
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using DALL-E."""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "OpenAI client not configured"
                }
            
            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1,
                **kwargs
            )
            
            return {
                "success": True,
                "image_url": response.data[0].url,
                "revised_prompt": response.data[0].revised_prompt,
                "model": model,
                "parameters": {
                    "size": size,
                    "quality": quality,
                    "style": style,
                },
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model,
            }
    
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "seo",
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze content for SEO, readability, etc."""
        
        system_messages = {
            "seo": "あなたはSEOの専門家です。コンテンツを分析し、改善提案を行ってください。",
            "readability": "あなたは文章の可読性の専門家です。読みやすさを分析してください。",
            "keyword_optimization": "あなたはキーワード最適化の専門家です。キーワードの使用状況を分析してください。",
        }
        
        analysis_prompts = {
            "seo": f"""
            以下のコンテンツをSEOの観点から分析し、JSON形式で回答してください：

            {content}

            分析項目：
            {{
                "seo_score": 0-100の数値,
                "keyword_density": {{"キーワード": 密度}},
                "readability_score": 0-100の数値,
                "title_optimization": "タイトルの評価とコメント",
                "meta_description_suggestion": "推奨メタディスクリプション",
                "heading_structure": "見出し構造の評価",
                "internal_linking": "内部リンクの提案",
                "suggestions": ["具体的な改善提案のリスト"]
            }}
            """,
            
            "readability": f"""
            以下のコンテンツの可読性を分析し、JSON形式で回答してください：

            {content}

            分析項目：
            {{
                "readability_score": 0-100の数値,
                "reading_level": "対象読者レベル",
                "sentence_complexity": "文の複雑さ評価",
                "paragraph_analysis": "段落構成の評価",
                "vocabulary_difficulty": "語彙の難易度",
                "flow_and_coherence": "文章の流れと一貫性",
                "suggestions": ["読みやすさ改善提案"]
            }}
            """,
            
            "keyword_optimization": f"""
            以下のコンテンツのキーワード最適化を分析し、JSON形式で回答してください：

            {content}

            分析項目：
            {{
                "primary_keywords": ["特定された主要キーワード"],
                "keyword_frequency": {{"キーワード": 出現回数}},
                "keyword_density": {{"キーワード": 密度}},
                "lsi_keywords": ["関連キーワードの提案"],
                "keyword_placement": "キーワード配置の評価",
                "optimization_opportunities": ["最適化の機会"],
                "suggestions": ["キーワード最適化提案"]
            }}
            """
        }
        
        system_message = system_messages.get(analysis_type, system_messages["seo"])
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["seo"])
        
        try:
            result = await self.generate_text(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                **kwargs
            )
            
            if result["success"]:
                # Try to parse JSON response
                import json
                try:
                    analysis_data = json.loads(result["content"])
                    result["analysis"] = analysis_data
                except json.JSONDecodeError:
                    result["analysis"] = {"raw_response": result["content"]}
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type,
            }
    
    async def generate_seo_content(
        self,
        topic: str,
        keywords: List[str],
        content_type: str = "blog_post",
        target_length: int = 2000,
        tone: str = "professional",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate SEO-optimized content."""
        
        keywords_str = "、".join(keywords)
        
        system_message = """
        あなたはSEOコンテンツの専門ライターです。
        検索エンジン最適化とユーザーエクスペリエンスの両方を考慮した、
        高品質なコンテンツを作成してください。
        """
        
        prompt = f"""
        以下の条件でSEO最適化されたコンテンツを作成してください：

        **基本情報:**
        - トピック: {topic}
        - メインキーワード: {keywords_str}
        - コンテンツタイプ: {content_type}
        - 目標文字数: {target_length}文字
        - トーン: {tone}

        **構成要件:**
        1. SEO最適化されたタイトル（32文字以内、キーワード含む）
        2. メタディスクリプション（120-160文字、魅力的で要約的）
        3. 導入部（読者の課題や関心を引く）
        4. 論理的な見出し構造（H2、H3の適切な使用）
        5. 価値提供する本文（専門性、権威性、信頼性を意識）
        6. 実用的なまとめ（次のアクション含む）
        7. 関連FAQ（最低5項目）

        **SEO要件:**
        - キーワード密度: 1-3%
        - 関連キーワードの自然な使用
        - E-A-T原則の遵守
        - ユーザーの検索意図への対応
        - 読みやすい文章構造

        コンテンツを作成してください。
        """
        
        try:
            result = await self.generate_text(
                prompt=prompt,
                system_message=system_message,
                max_tokens=target_length * 2,
                temperature=0.8,
                **kwargs
            )
            
            if result["success"]:
                content = result["content"]
                
                # Extract structured information
                result["structured_content"] = {
                    "full_content": content,
                    "topic": topic,
                    "keywords": keywords,
                    "estimated_length": len(content),
                    "content_type": content_type,
                    "tone": tone,
                }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "keywords": keywords,
            }
    
    async def test_connection(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Test the API connection and return status."""
        try:
            test_key = api_key or self.api_key
            if not test_key:
                return {
                    "success": False,
                    "error": "API key not provided"
                }
            
            # Create temporary client for testing
            test_client = AsyncOpenAI(api_key=test_key)
            
            # Test with a simple prompt
            response = await test_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for testing
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, please respond with 'Connection successful' if you can read this."
                    }
                ],
                max_tokens=50
            )
            
            return {
                "success": True,
                "message": "OpenAI API connection successful",
                "model": "gpt-3.5-turbo",
                "response": response.choices[0].message.content,
                "usage": {
                    "total_tokens": response.usage.total_tokens,
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenAI API test failed: {str(e)}"
            }