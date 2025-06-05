"""AI Service Manager for coordinating multiple AI providers."""

import asyncio
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.models.api_key import APIKey, APIProvider
from app.services.api_key_service import APIKeyService
from .anthropic_service import AnthropicService
from .gemini_service import GeminiService
from .openai_service import OpenAIService


class AIServiceManager:
    """Manager for coordinating multiple AI services with fallback support."""
    
    def __init__(self, db: Session, user_id: int):
        """Initialize AI service manager for a specific user."""
        self.db = db
        self.user_id = user_id
        self.api_key_service = APIKeyService(db)
        
        # Initialize services
        self.services = {
            APIProvider.GOOGLE_GEMINI: GeminiService(),
            APIProvider.OPENAI: OpenAIService(),
            APIProvider.ANTHROPIC: AnthropicService(),
        }
        
        # Load user's API keys
        self._load_user_api_keys()
    
    def _load_user_api_keys(self) -> None:
        """Load and configure API keys for the user."""
        api_keys = self.api_key_service.get_api_keys(
            user_id=self.user_id,
            is_active=True,
            is_verified=True
        )
        
        for api_key in api_keys:
            if api_key.provider in self.services:
                service = self.services[api_key.provider]
                service.configure_with_api_key(api_key)
    
    def get_available_providers(self) -> List[APIProvider]:
        """Get list of available providers with valid API keys."""
        available = []
        
        for provider, service in self.services.items():
            if service.api_key:
                available.append(provider)
        
        return available
    
    def get_service(self, provider: APIProvider) -> Optional[Union[GeminiService, OpenAIService, AnthropicService]]:
        """Get service instance for a specific provider."""
        return self.services.get(provider)
    
    async def generate_text(
        self,
        prompt: str,
        provider: Optional[APIProvider] = None,
        fallback_providers: Optional[List[APIProvider]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text with primary provider and fallback support."""
        
        # Determine providers to try
        providers_to_try = []
        
        if provider:
            providers_to_try.append(provider)
        
        if fallback_providers:
            providers_to_try.extend(fallback_providers)
        
        # If no specific providers, try all available
        if not providers_to_try:
            providers_to_try = self.get_available_providers()
        
        # Default fallback order if not specified
        if not providers_to_try:
            providers_to_try = [
                APIProvider.GOOGLE_GEMINI,
                APIProvider.ANTHROPIC,
                APIProvider.OPENAI,
            ]
        
        last_error = None
        
        for provider_type in providers_to_try:
            service = self.get_service(provider_type)
            
            if not service or not service.api_key:
                continue
            
            try:
                # Check usage limits first
                if not self._check_usage_limits(provider_type):
                    continue
                
                result = await service.generate_text(prompt, **kwargs)
                
                if result["success"]:
                    # Update usage tracking
                    await self._update_usage(provider_type, result.get("usage", {}))
                    
                    result["provider_used"] = provider_type.value
                    return result
                else:
                    last_error = result.get("error", "Unknown error")
                    
            except Exception as e:
                last_error = str(e)
                continue
        
        return {
            "success": False,
            "error": f"All providers failed. Last error: {last_error}",
            "providers_tried": [p.value for p in providers_to_try]
        }
    
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "seo",
        provider: Optional[APIProvider] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze content with fallback support."""
        
        # Prefer Claude for analysis tasks due to its reasoning capabilities
        preferred_providers = [
            APIProvider.ANTHROPIC,
            APIProvider.GOOGLE_GEMINI,
            APIProvider.OPENAI,
        ]
        
        if provider:
            preferred_providers = [provider] + [p for p in preferred_providers if p != provider]
        
        return await self._execute_with_fallback(
            "analyze_content",
            preferred_providers,
            content=content,
            analysis_type=analysis_type,
            **kwargs
        )
    
    async def generate_seo_content(
        self,
        topic: str,
        keywords: List[str],
        content_type: str = "blog_post",
        target_length: int = 2000,
        tone: str = "professional",
        provider: Optional[APIProvider] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate SEO content with fallback support."""
        
        # Prefer Claude and Gemini for content generation
        preferred_providers = [
            APIProvider.ANTHROPIC,
            APIProvider.GOOGLE_GEMINI,
            APIProvider.OPENAI,
        ]
        
        if provider:
            preferred_providers = [provider] + [p for p in preferred_providers if p != provider]
        
        return await self._execute_with_fallback(
            "generate_seo_content",
            preferred_providers,
            topic=topic,
            keywords=keywords,
            content_type=content_type,
            target_length=target_length,
            tone=tone,
            **kwargs
        )
    
    async def generate_image(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using OpenAI DALL-E (primary image generation provider)."""
        
        openai_service = self.get_service(APIProvider.OPENAI)
        
        if not openai_service or not openai_service.api_key:
            return {
                "success": False,
                "error": "OpenAI service not configured for image generation"
            }
        
        try:
            # Check usage limits
            if not self._check_usage_limits(APIProvider.OPENAI):
                return {
                    "success": False,
                    "error": "Usage limit exceeded for OpenAI"
                }
            
            result = await openai_service.generate_image(prompt, **kwargs)
            
            if result["success"]:
                # Update usage tracking (approximate tokens for image generation)
                await self._update_usage(APIProvider.OPENAI, {"total_tokens": 1000})
                result["provider_used"] = APIProvider.OPENAI.value
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": APIProvider.OPENAI.value
            }
    
    async def test_all_connections(self) -> Dict[str, Any]:
        """Test connections for all configured providers."""
        results = {}
        
        for provider, service in self.services.items():
            if service.api_key:
                try:
                    result = await service.test_connection()
                    results[provider.value] = result
                except Exception as e:
                    results[provider.value] = {
                        "success": False,
                        "error": str(e)
                    }
            else:
                results[provider.value] = {
                    "success": False,
                    "error": "API key not configured"
                }
        
        return results
    
    async def _execute_with_fallback(
        self,
        method_name: str,
        providers: List[APIProvider],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a method with fallback providers."""
        
        last_error = None
        
        for provider_type in providers:
            service = self.get_service(provider_type)
            
            if not service or not service.api_key:
                continue
            
            try:
                # Check usage limits
                if not self._check_usage_limits(provider_type):
                    continue
                
                method = getattr(service, method_name)
                result = await method(**kwargs)
                
                if result["success"]:
                    # Update usage tracking
                    await self._update_usage(provider_type, result.get("usage", {}))
                    
                    result["provider_used"] = provider_type.value
                    return result
                else:
                    last_error = result.get("error", "Unknown error")
                    
            except Exception as e:
                last_error = str(e)
                continue
        
        return {
            "success": False,
            "error": f"All providers failed. Last error: {last_error}",
            "providers_tried": [p.value for p in providers]
        }
    
    def _check_usage_limits(self, provider: APIProvider) -> bool:
        """Check if provider is within usage limits."""
        try:
            api_keys = self.api_key_service.get_api_keys(
                user_id=self.user_id,
                provider=provider,
                is_active=True
            )
            
            for api_key in api_keys:
                usage_check = self.api_key_service.check_usage_limits(api_key.id)
                if usage_check["allowed"]:
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _update_usage(self, provider: APIProvider, usage_data: Dict[str, Any]) -> None:
        """Update usage tracking for provider."""
        try:
            api_keys = self.api_key_service.get_api_keys(
                user_id=self.user_id,
                provider=provider,
                is_active=True
            )
            
            if api_keys:
                # Use the first active API key for this provider
                api_key = api_keys[0]
                tokens_used = usage_data.get("total_tokens", 0)
                
                if tokens_used > 0:
                    self.api_key_service.update_usage(api_key.id, tokens_used)
                    
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to update usage for {provider}: {e}")
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for all providers."""
        stats = {}
        
        for provider in APIProvider:
            try:
                api_keys = self.api_key_service.get_api_keys(
                    user_id=self.user_id,
                    provider=provider
                )
                
                if api_keys:
                    api_key = api_keys[0]  # Use first key for stats
                    stats[provider.value] = {
                        "configured": True,
                        "active": api_key.is_active,
                        "verified": api_key.is_verified,
                        "daily_usage": api_key.daily_usage,
                        "daily_limit": api_key.daily_limit,
                        "monthly_usage": api_key.monthly_usage,
                        "monthly_limit": api_key.monthly_limit,
                        "last_used": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
                    }
                else:
                    stats[provider.value] = {
                        "configured": False,
                        "active": False,
                        "verified": False,
                    }
                    
            except Exception:
                stats[provider.value] = {
                    "configured": False,
                    "error": "Failed to retrieve statistics"
                }
        
        return stats