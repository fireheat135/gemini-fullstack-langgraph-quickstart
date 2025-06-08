"""
User management API endpoints
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.api.deps import get_current_user, get_current_active_user
from src.models.user import User
from src.schemas.user import UserResponse, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user info"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user info"""
    # Update user fields
    if user_update.name is not None:
        current_user.name = user_update.name
    
    db.commit()
    db.refresh(current_user)
    
    return current_user