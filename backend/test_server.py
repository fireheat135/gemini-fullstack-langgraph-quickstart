#!/usr/bin/env python3
"""Simple test server to verify API endpoints."""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from src.main import app
    print("✅ FastAPI app imported successfully")
    
    # Check if essential environment variables are set
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        print(f"✅ GEMINI_API_KEY found: {gemini_key[:10]}...")
    else:
        print("⚠️  GEMINI_API_KEY not found")
    
    secret_key = os.getenv('SECRET_KEY')
    if secret_key:
        print(f"✅ SECRET_KEY found: {secret_key[:10]}...")
    else:
        print("⚠️  SECRET_KEY not found")
    
    print("\n🚀 Starting test server on http://localhost:8123")
    print("📋 API docs will be available at: http://localhost:8123/docs")
    print("🔍 Health check: http://localhost:8123/health")
    
    if __name__ == "__main__":
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8123,
            log_level="info",
            reload=False
        )
        
except ImportError as e:
    print(f"❌ Failed to import FastAPI app: {e}")
except Exception as e:
    print(f"❌ Error starting server: {e}")