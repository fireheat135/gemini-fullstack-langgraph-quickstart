"""Authentication API endpoints."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import create_access_token, verify_token
from ..db.deps import get_db
from ..models.user import User
from ..schemas.token import Token
from ..schemas.user import UserCreate, UserLogin, User as UserSchema
from ..services.user_service import UserService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception
    
    user_service = UserService(db)
    user = user_service.get(int(user_id))
    if user is None:
        raise credentials_exception
    
    if not user_service.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Register new user."""
    user_service = UserService(db)
    
    # Check if user already exists
    user = user_service.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create user data dict
    user_data = user_in.model_dump()
    user = user_service.create(user_data)
    return user


@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user_service = UserService(db)
    user = user_service.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user_service.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Update last login
    user_service.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login/simple", response_model=Token)
def login_simple(
    *,
    db: Session = Depends(get_db),
    user_credentials: UserLogin,
) -> Any:
    """Simple login with email and password."""
    user_service = UserService(db)
    user = user_service.authenticate(
        email=user_credentials.email, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user_service.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Update last login
    user_service.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user."""
    return current_user


@router.post("/test-token", response_model=UserSchema)
def test_token(current_user: User = Depends(get_current_user)) -> Any:
    """Test access token."""
    return current_user