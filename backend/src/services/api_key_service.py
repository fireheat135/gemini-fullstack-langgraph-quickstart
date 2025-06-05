"""API Key service for managing external service credentials."""

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from ..models.api_key import APIKey, APIProvider
from ..schemas.api_key import APIKeyCreate, APIKeyUpdate
from ..core.encryption import encrypt_api_key, decrypt_api_key


class APIKeyService:
    """Service for managing API keys."""

    def __init__(self, db: Session):
        self.db = db

    def get_api_key(self, api_key_id: int) -> Optional[APIKey]:
        """Get API key by ID."""
        return self.db.query(APIKey).filter(APIKey.id == api_key_id).first()

    def get_api_keys(
        self,
        user_id: int,
        provider: Optional[APIProvider] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None
    ) -> List[APIKey]:
        """Get API keys for a user with optional filters."""
        query = self.db.query(APIKey).filter(APIKey.user_id == user_id)
        
        if provider:
            query = query.filter(APIKey.provider == provider)
        if is_active is not None:
            query = query.filter(APIKey.is_active == is_active)
        if is_verified is not None:
            query = query.filter(APIKey.is_verified == is_verified)
        
        return query.all()

    def create_api_key(self, user_id: int, api_key_create: APIKeyCreate) -> APIKey:
        """Create a new API key."""
        # Encrypt the API key before storing
        encrypted_key = encrypt_api_key(api_key_create.api_key)
        
        db_api_key = APIKey(
            user_id=user_id,
            provider=api_key_create.provider,
            name=api_key_create.name,
            encrypted_api_key=encrypted_key,
            model_name=api_key_create.model_name,
            max_tokens=api_key_create.max_tokens,
            temperature=api_key_create.temperature,
            daily_limit=api_key_create.daily_limit,
            monthly_limit=api_key_create.monthly_limit,
        )
        
        self.db.add(db_api_key)
        self.db.commit()
        self.db.refresh(db_api_key)
        return db_api_key

    def update_api_key(
        self, 
        api_key_id: int, 
        api_key_update: APIKeyUpdate
    ) -> Optional[APIKey]:
        """Update API key information."""
        db_api_key = self.get_api_key(api_key_id)
        if not db_api_key:
            return None

        update_data = api_key_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_api_key, field, value)

        self.db.commit()
        self.db.refresh(db_api_key)
        return db_api_key

    def delete_api_key(self, api_key_id: int) -> bool:
        """Delete an API key."""
        db_api_key = self.get_api_key(api_key_id)
        if not db_api_key:
            return False

        self.db.delete(db_api_key)
        self.db.commit()
        return True

    def get_decrypted_api_key(self, api_key_id: int) -> Optional[str]:
        """Get decrypted API key for use."""
        db_api_key = self.get_api_key(api_key_id)
        if not db_api_key or not db_api_key.is_active:
            return None

        try:
            return decrypt_api_key(db_api_key.encrypted_api_key)
        except Exception:
            return None

    def test_api_key(self, api_key_id: int) -> Dict[str, Any]:
        """Test API key connectivity."""
        db_api_key = self.get_api_key(api_key_id)
        if not db_api_key:
            return {"success": False, "error": "API key not found"}

        decrypted_key = self.get_decrypted_api_key(api_key_id)
        if not decrypted_key:
            return {"success": False, "error": "Failed to decrypt API key"}

        # Here you would implement actual API testing based on provider
        # For now, return a mock response
        try:
            # This would be replaced with actual API calls
            test_result = self._test_provider_connection(
                db_api_key.provider, 
                decrypted_key
            )
            
            if test_result["success"]:
                db_api_key.is_verified = True
                db_api_key.last_error = None
            else:
                db_api_key.is_verified = False
                db_api_key.last_error = test_result.get("error")
            
            self.db.commit()
            return test_result
            
        except Exception as e:
            db_api_key.is_verified = False
            db_api_key.last_error = str(e)
            self.db.commit()
            return {"success": False, "error": str(e)}

    def update_usage(self, api_key_id: int, tokens_used: int) -> bool:
        """Update API key usage statistics."""
        db_api_key = self.get_api_key(api_key_id)
        if not db_api_key:
            return False

        db_api_key.daily_usage += tokens_used
        db_api_key.monthly_usage += tokens_used
        db_api_key.total_usage += tokens_used
        db_api_key.last_used_at = datetime.utcnow()

        self.db.commit()
        return True

    def check_usage_limits(self, api_key_id: int) -> Dict[str, Any]:
        """Check if API key usage is within limits."""
        db_api_key = self.get_api_key(api_key_id)
        if not db_api_key:
            return {"allowed": False, "reason": "API key not found"}

        if not db_api_key.is_active:
            return {"allowed": False, "reason": "API key is inactive"}

        # Check daily limit
        if db_api_key.daily_limit and db_api_key.daily_usage >= db_api_key.daily_limit:
            return {"allowed": False, "reason": "Daily limit exceeded"}

        # Check monthly limit
        if db_api_key.monthly_limit and db_api_key.monthly_usage >= db_api_key.monthly_limit:
            return {"allowed": False, "reason": "Monthly limit exceeded"}

        return {
            "allowed": True,
            "daily_remaining": (
                db_api_key.daily_limit - db_api_key.daily_usage
                if db_api_key.daily_limit else None
            ),
            "monthly_remaining": (
                db_api_key.monthly_limit - db_api_key.monthly_usage
                if db_api_key.monthly_limit else None
            ),
        }

    def reset_daily_usage(self) -> int:
        """Reset daily usage for all API keys (to be called daily)."""
        updated_count = self.db.query(APIKey).update({"daily_usage": 0})
        self.db.commit()
        return updated_count

    def reset_monthly_usage(self) -> int:
        """Reset monthly usage for all API keys (to be called monthly)."""
        updated_count = self.db.query(APIKey).update({"monthly_usage": 0})
        self.db.commit()
        return updated_count

    def _test_provider_connection(
        self, 
        provider: APIProvider, 
        api_key: str
    ) -> Dict[str, Any]:
        """Test connection to specific provider."""
        # This is a mock implementation
        # In a real application, you would make actual API calls
        # to test the connectivity
        
        if provider == APIProvider.GOOGLE_GEMINI:
            return {"success": True, "provider": "Google Gemini", "model": "gemini-pro"}
        elif provider == APIProvider.OPENAI:
            return {"success": True, "provider": "OpenAI", "model": "gpt-3.5-turbo"}
        elif provider == APIProvider.ANTHROPIC:
            return {"success": True, "provider": "Anthropic", "model": "claude-3-sonnet"}
        else:
            return {"success": False, "error": "Unknown provider"}