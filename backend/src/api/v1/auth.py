"""
Authentication API endpoints
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import httpx

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.db.deps import get_db
from src.models.user import User
from src.core.config import settings
from src.schemas.token import Token, TokenData
from src.schemas.user import UserCreate


router = APIRouter(prefix="/auth", tags=["authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Ensure database tables exist
    try:
        from src.db.session import init_db as create_tables
        create_tables()
    except Exception as e:
        print(f"Table creation: {e}")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.email,  # Use email as username
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/google")
async def google_auth():
    """Start Google OAuth2 flow"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth2 not configured"
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Google OAuth2 authorization URL - redirect to backend, not frontend
    backend_url = "https://scrib-ai-writing-superpowers-263183603168.us-west1.run.app"
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        "response_type=code&"
        f"redirect_uri={backend_url}/api/v1/auth/google/callback&"
        "scope=openid email profile&"
        f"state={state}"
    )
    
    return {
        "auth_url": google_auth_url,
        "state": state
    }


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth2 callback"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth2 not configured"
        )
    
    try:
        # Exchange code for access token
        backend_url = "https://scrib-ai-writing-superpowers-263183603168.us-west1.run.app"
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{backend_url}/api/v1/auth/google/callback"
                }
            )
            token_data = token_response.json()
            
            # Debug: log the response from Google
            print(f"Google token response status: {token_response.status_code}")
            print(f"Google token response: {token_data}")
            
            if "access_token" not in token_data:
                error_detail = token_data.get("error_description", token_data.get("error", "Unknown error"))
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get access token from Google: {error_detail}"
                )
            
            # Get user info from Google
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            user_info = user_response.json()
        
        # Check if user exists
        user = db.query(User).filter(User.email == user_info["email"]).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_info["email"],
                username=user_info["email"],
                name=user_info.get("name", ""),
                hashed_password="",  # No password for OAuth users
                is_active=True,
                is_verified=True,
                oauth_provider="google",
                oauth_id=user_info["id"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update OAuth info if not set
            if not user.oauth_provider:
                user.oauth_provider = "google"
                user.oauth_id = user_info["id"]
                user.is_verified = True
                db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token
        frontend_url = "https://scrib-ai-writing-superpowers-frontend-263183603168.us-west1.run.app"
        from fastapi.responses import RedirectResponse
        
        # Redirect to frontend with token as query parameter
        redirect_url = f"{frontend_url}?token={access_token}&type=bearer"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        print(f"Google OAuth2 error: {str(e)}")
        # Redirect to frontend with error
        frontend_url = "https://scrib-ai-writing-superpowers-frontend-263183603168.us-west1.run.app"
        from fastapi.responses import RedirectResponse
        
        redirect_url = f"{frontend_url}?error=oauth_failed&message={str(e)}"
        return RedirectResponse(url=redirect_url)