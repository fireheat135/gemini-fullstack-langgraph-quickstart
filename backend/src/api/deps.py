"""
API dependencies
"""
from typing import Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.deps import get_db
from src.models.user import User
from src.models.api_key import APIKey, APIProvider
from src.core.encryption import encrypt_value


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class TokenData(BaseModel):
    username: Optional[str] = None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    # Check if authentication is bypassed (development mode)
    if settings.AUTH_BYPASS:
        # Create or get a mock user for development
        mock_user = db.query(User).filter(User.email == "dev@example.com").first()
        if not mock_user:
            # Create a mock user
            mock_user = User(
                email="dev@example.com",
                name="Development User",
                is_active=True,
                is_superuser=False,
                hashed_password="mock_password_hash"
            )
            db.add(mock_user)
            db.commit()
            db.refresh(mock_user)
        
        # Ensure user has API keys
        ensure_dev_user_has_api_keys(mock_user, db)
        return mock_user
    
    # Normal authentication flow
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def ensure_dev_user_has_api_keys(user: User, db: Session) -> None:
    """Ensure development user has necessary API keys"""
    if settings.AUTH_BYPASS and user.email == "dev@example.com":
        # Check if Gemini API key exists
        existing_key = db.query(APIKey).filter(
            APIKey.user_id == user.id,
            APIKey.provider == APIProvider.GOOGLE_GEMINI
        ).first()
        
        if not existing_key and settings.GEMINI_API_KEY:
            # Create API key for development user
            api_key = APIKey(
                user_id=user.id,
                provider=APIProvider.GOOGLE_GEMINI,
                name="Development Gemini API Key",
                encrypted_api_key=encrypt_value(settings.GEMINI_API_KEY),
                is_active=True
            )
            db.add(api_key)
            db.commit()