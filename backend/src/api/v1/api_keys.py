"""
API Key management endpoints
"""
from typing import List
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import google.generativeai as genai
import openai
import anthropic

from src.db.deps import get_db
from src.api.deps import get_current_active_user
from src.models.user import User
from src.models.api_key import APIKey, APIProvider
from src.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyUpdate
from src.core.encryption import encrypt_value, decrypt_value


router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List user's API keys"""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    
    # Don't return actual keys, just metadata
    return [
        APIKeyResponse(
            id=key.id,
            provider=key.provider,
            is_active=key.is_active,
            created_at=key.created_at,
            updated_at=key.updated_at
        )
        for key in api_keys
    ]


@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    # Check if key already exists for this provider
    existing_key = db.query(APIKey).filter(
        APIKey.user_id == current_user.id,
        APIKey.provider == api_key_data.provider
    ).first()
    
    if existing_key:
        raise HTTPException(
            status_code=400,
            detail=f"API key for {api_key_data.provider} already exists"
        )
    
    # Encrypt the API key
    encrypted_key = encrypt_value(api_key_data.api_key)
    
    # Create new API key
    api_key = APIKey(
        user_id=current_user.id,
        provider=api_key_data.provider,
        encrypted_key=encrypted_key,
        is_active=True
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return APIKeyResponse(
        id=api_key.id,
        provider=api_key.provider,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at
    )


@router.put("/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: int,
    api_key_update: APIKeyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an API key"""
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Update fields
    if api_key_update.api_key is not None:
        api_key.encrypted_key = encrypt_value(api_key_update.api_key)
    
    if api_key_update.is_active is not None:
        api_key.is_active = api_key_update.is_active
    
    db.commit()
    db.refresh(api_key)
    
    return APIKeyResponse(
        id=api_key.id,
        provider=api_key.provider,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at
    )


@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(api_key)
    db.commit()
    
    return {"detail": "API key deleted successfully"}


@router.post("/{api_key_id}/test")
async def test_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Test API key connectivity and validity"""
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    if not api_key.is_active:
        raise HTTPException(status_code=400, detail="API key is not active")
    
    # Decrypt the API key
    try:
        decrypted_key = decrypt_value(api_key.encrypted_key)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to decrypt API key")
    
    # Test the API key based on provider
    test_result = {"provider": api_key.provider.value, "status": "unknown", "message": ""}
    
    try:
        if api_key.provider == APIProvider.GEMINI:
            # Test Gemini API
            genai.configure(api_key=decrypted_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Test connection")
            if response.text:
                test_result["status"] = "success"
                test_result["message"] = "Gemini API key is valid and working"
            else:
                test_result["status"] = "error"
                test_result["message"] = "Gemini API returned empty response"
                
        elif api_key.provider == APIProvider.OPENAI:
            # Test OpenAI API
            client = openai.OpenAI(api_key=decrypted_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=5
            )
            if response.choices:
                test_result["status"] = "success"
                test_result["message"] = "OpenAI API key is valid and working"
            else:
                test_result["status"] = "error"
                test_result["message"] = "OpenAI API returned no choices"
                
        elif api_key.provider == APIProvider.ANTHROPIC:
            # Test Anthropic API
            client = anthropic.Anthropic(api_key=decrypted_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Test connection"}]
            )
            if response.content:
                test_result["status"] = "success"
                test_result["message"] = "Anthropic API key is valid and working"
            else:
                test_result["status"] = "error"
                test_result["message"] = "Anthropic API returned empty content"
                
        else:
            test_result["status"] = "error"
            test_result["message"] = f"Testing not implemented for provider: {api_key.provider.value}"
            
    except Exception as e:
        test_result["status"] = "error"
        test_result["message"] = f"API test failed: {str(e)}"
    
    return test_result