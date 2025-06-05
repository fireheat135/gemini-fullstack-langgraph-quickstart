"""Google Gemini AI service integration."""

import asyncio
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.config import settings
from app.models.api_key import APIKey


class GeminiService:
    """Service for Google Gemini AI integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service with API key."""
        self.api_key = api_key or settings.GOOGLE_GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    @property
    def default_model(self) -> str:
        """Default Gemini model to use."""
        return "gemini-2.5-flash-preview-05-20"
    
    @property
    def available_models(self) -> List[str]:
        """List of available Gemini models."""
        return [
            "gemini-2.5-flash-preview-05-20",
            "gemini-2.5-pro-preview-05-06", 
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
    
    def configure_with_api_key(self, api_key_obj: APIKey) -> None:
        """Configure service with encrypted API key object."""
        from app.core.encryption import decrypt_api_key
        
        decrypted_key = decrypt_api_key(api_key_obj.encrypted_api_key)
        self.api_key = decrypted_key
        genai.configure(api_key=self.api_key)
    
    async def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Gemini API."""
        try:
            model_name = model_name or self.default_model
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens or 8192,
                temperature=temperature or 0.7,
                top_p=0.8,
                top_k=40
            )
            
            # Safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # Initialize model
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Generate content
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                **kwargs
            )
            
            return {
                "success": True,
                "content": response.text,
                "model": model_name,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
                    "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0,
                },
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else None,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_name or self.default_model,
            }
    
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "seo",
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze content for SEO, readability, etc."""
        
        analysis_prompts = {
            "seo": f"""
            以下のコンテンツをSEOの観点から分析してください：

            {content}

            以下の項目について評価し、JSON形式で回答してください：
            {{
                "seo_score": 0-100の数値,
                "keyword_density": {{"キーワード": 密度の割合}},
                "readability_score": 0-100の数値,
                "suggestions": ["改善提案1", "改善提案2", ...],
                "title_suggestions": ["タイトル案1", "タイトル案2", ...],
                "meta_description": "推奨メタディスクリプション"
            }}
            """,
            
            "readability": f"""
            以下のコンテンツの可読性を分析してください：

            {content}

            以下の項目について評価し、JSON形式で回答してください：
            {{
                "readability_score": 0-100の数値,
                "reading_level": "小学生/中学生/高校生/大学生/専門家",
                "sentence_length_avg": 平均文字数,
                "paragraph_count": 段落数,
                "suggestions": ["改善提案1", "改善提案2", ...]
            }}
            """,
            
            "keyword_optimization": f"""
            以下のコンテンツのキーワード最適化を分析してください：

            {content}

            以下の項目について評価し、JSON形式で回答してください：
            {{
                "primary_keywords": ["主要キーワード1", "主要キーワード2"],
                "keyword_distribution": {{"キーワード": 出現回数}},
                "lsi_keywords": ["関連キーワード1", "関連キーワード2"],
                "optimization_score": 0-100の数値,
                "suggestions": ["改善提案1", "改善提案2", ...]
            }}
            """
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["seo"])
        
        try:
            result = await self.generate_text(
                prompt=prompt,
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
        
        prompt = f"""
        以下の条件でSEO最適化されたコンテンツを作成してください：

        トピック: {topic}
        メインキーワード: {keywords_str}
        コンテンツタイプ: {content_type}
        目標文字数: {target_length}文字
        トーン: {tone}

        以下の構造で作成してください：
        1. 魅力的なタイトル（SEOキーワード含む）
        2. メタディスクリプション（160文字以内）
        3. 導入部（問題提起、読者の関心を引く）
        4. 見出し構造（H2、H3を適切に使用）
        5. 本文（各セクションでキーワードを自然に使用）
        6. まとめ（CTA含む）
        7. FAQ（よくある質問、5つ以上）

        要件：
        - キーワード密度は1-3%
        - 読みやすい文章構造
        - 価値のある情報を提供
        - E-A-T（専門性、権威性、信頼性）を意識
        - ユーザーの検索意図に対応
        """
        
        try:
            result = await self.generate_text(
                prompt=prompt,
                max_tokens=target_length * 2,  # Allow for longer generation
                temperature=0.8,
                **kwargs
            )
            
            if result["success"]:
                # Parse the generated content structure
                content = result["content"]
                
                # Extract title, meta description, etc. if needed
                result["structured_content"] = {
                    "full_content": content,
                    "topic": topic,
                    "keywords": keywords,
                    "estimated_length": len(content),
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
            
            # Temporarily configure with test key
            original_key = self.api_key
            genai.configure(api_key=test_key)
            
            try:
                # Test with a simple prompt
                model = genai.GenerativeModel(self.default_model)
                response = await asyncio.to_thread(
                    model.generate_content,
                    "Hello, please respond with 'Connection successful' if you can read this."
                )
                
                return {
                    "success": True,
                    "message": "Google Gemini API connection successful",
                    "model": self.default_model,
                    "response": response.text[:100] + "..." if len(response.text) > 100 else response.text,
                }
                
            finally:
                # Restore original key
                if original_key:
                    genai.configure(api_key=original_key)
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Google Gemini API test failed: {str(e)}"
            }