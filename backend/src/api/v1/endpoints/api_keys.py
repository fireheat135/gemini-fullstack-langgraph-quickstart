"""API Keys management endpoints."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....db.deps import get_db
from ....schemas.api_key import APIKey, APIKeyCreate, APIKeyUpdate, APIKeyTest, APIKeyWithUsage
from ....schemas.user import User
from ....services.api_key_service import APIKeyService
from .auth import get_current_active_user

router = APIRouter()


@router.get("", response_model=List[APIKeyWithUsage])
def read_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Retrieve API keys for the current user."""
    api_key_service = APIKeyService(db)
    api_keys = api_key_service.get_api_keys(user_id=current_user.id)
    
    # Add usage statistics
    api_keys_with_usage = []
    for api_key in api_keys:
        usage_stats = {}
        
        # Calculate usage percentages
        if api_key.daily_limit:
            usage_stats["usage_percentage_daily"] = (
                api_key.daily_usage / api_key.daily_limit * 100
            )
            usage_stats["remaining_daily"] = api_key.daily_limit - api_key.daily_usage
        
        if api_key.monthly_limit:
            usage_stats["usage_percentage_monthly"] = (
                api_key.monthly_usage / api_key.monthly_limit * 100
            )
            usage_stats["remaining_monthly"] = api_key.monthly_limit - api_key.monthly_usage
        
        api_key_with_usage = APIKeyWithUsage(**api_key.__dict__, **usage_stats)
        api_keys_with_usage.append(api_key_with_usage)
    
    return api_keys_with_usage


@router.post("", response_model=APIKey)
def create_api_key(
    api_key_create: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new API key."""
    api_key_service = APIKeyService(db)
    api_key = api_key_service.create_api_key(
        user_id=current_user.id,
        api_key_create=api_key_create
    )
    return api_key


@router.get("/{api_key_id}", response_model=APIKeyWithUsage)
def read_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get API key by ID."""
    api_key_service = APIKeyService(db)
    api_key = api_key_service.get_api_key(api_key_id=api_key_id)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check ownership
    if api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Add usage statistics
    usage_stats = {}
    if api_key.daily_limit:
        usage_stats["usage_percentage_daily"] = (
            api_key.daily_usage / api_key.daily_limit * 100
        )
        usage_stats["remaining_daily"] = api_key.daily_limit - api_key.daily_usage
    
    if api_key.monthly_limit:
        usage_stats["usage_percentage_monthly"] = (
            api_key.monthly_usage / api_key.monthly_limit * 100
        )
        usage_stats["remaining_monthly"] = api_key.monthly_limit - api_key.monthly_usage
    
    return APIKeyWithUsage(**api_key.__dict__, **usage_stats)


@router.put("/{api_key_id}", response_model=APIKey)
def update_api_key(
    api_key_id: int,
    api_key_update: APIKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update API key."""
    api_key_service = APIKeyService(db)
    api_key = api_key_service.get_api_key(api_key_id=api_key_id)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check ownership
    if api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    api_key = api_key_service.update_api_key(
        api_key_id=api_key_id,
        api_key_update=api_key_update
    )
    return api_key


@router.delete("/{api_key_id}")
def delete_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete API key."""
    api_key_service = APIKeyService(db)
    api_key = api_key_service.get_api_key(api_key_id=api_key_id)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check ownership
    if api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = api_key_service.delete_api_key(api_key_id=api_key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key"
        )
    
    return {"message": "API key deleted successfully"}


@router.post("/{api_key_id}/test", response_model=APIKeyTest)
def test_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Test API key connectivity."""
    api_key_service = APIKeyService(db)
    api_key = api_key_service.get_api_key(api_key_id=api_key_id)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check ownership
    if api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    test_result = api_key_service.test_api_key(api_key_id=api_key_id)
    return APIKeyTest(**test_result)