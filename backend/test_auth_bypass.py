#!/usr/bin/env python3
"""Test script to verify auth bypass functionality"""

import os
import sys
import sqlite3
import requests

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment variables for testing
os.environ['AUTH_BYPASS'] = 'true'
os.environ['DATABASE_URL'] = 'sqlite:///./test_auth_bypass.db'
os.environ['GEMINI_API_KEY'] = 'AIzaSyB1Ac8KV8aRdvZ2uEVaTRQZ59adfBp8k-M'
os.environ['SECRET_KEY'] = 'test-secret-key'

def test_auth_bypass():
    """Test that auth bypass is working"""
    from src.core.config import settings
    from src.api.deps import get_current_user
    from src.db.session import SessionLocal
    from src.models.user import User
    from src.models.api_key import APIKey
    from src.db.deps import get_db
    
    print(f"AUTH_BYPASS setting: {settings.AUTH_BYPASS}")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Create database and tables
    db = SessionLocal()
    try:
        # Create tables
        from src.models.base import Base
        from sqlalchemy import create_engine
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        
        # Test get_current_user without authentication
        user = get_current_user(token=None, db=db)
        print(f"Retrieved user: {user.email}, {user.name}")
        
        # Check if API key was created
        api_keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
        print(f"API keys for user: {len(api_keys)}")
        for key in api_keys:
            print(f"  - Provider: {key.provider}, Active: {key.is_active}")
        
        print("✅ Auth bypass test successful!")
        
    except Exception as e:
        print(f"❌ Auth bypass test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_auth_bypass()