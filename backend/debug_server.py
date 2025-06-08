#!/usr/bin/env python3
"""Debug server to test API imports."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, 'src')

try:
    print("Testing API router imports...")
    
    from api.v1.auth import router as auth_router
    print("✅ auth router imported successfully")
    
    from api.v1.users import router as users_router
    print("✅ users router imported successfully")
    
    from api.v1.api_keys import router as api_keys_router
    print("✅ api_keys router imported successfully")
    
    from api.v1.keywords import router as keywords_router
    print("✅ keywords router imported successfully")
    
    from api.v1.seo_research import router as seo_research_router
    print("✅ seo_research router imported successfully")
    
    from api.v1.content import router as content_router
    print("✅ content router imported successfully")
    
    from api.v1.analytics import router as analytics_router
    print("✅ analytics router imported successfully")
    
    print("\n✅ All API routers imported successfully!")
    
    # Test database initialization
    try:
        from db.init_db import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
    
    # Start the server with verbose logging
    print("\n🚀 Starting server with debug logging...")
    from agent.app import app
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8123,
        log_level="debug",
        reload=False
    )
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()