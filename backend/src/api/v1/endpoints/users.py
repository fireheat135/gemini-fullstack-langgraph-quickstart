"""User management endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....db.deps import get_db
from ....schemas.user import User, UserUpdate
from ....services.user_service import UserService
from .auth import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user."""
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update current user."""
    user_service = UserService(db)
    user = user_service.update_user(
        user_id=current_user.id,
        user_update=user_update
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user by ID (admin only or same user)."""
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    user = user_service.get_user(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user