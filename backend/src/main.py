"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
from src.api.v1.api_keys import router as api_keys_router
from src.api.v1.keywords import router as keywords_router
from src.api.v1.seo_research import router as seo_research_router
from src.api.v1.content import router as content_router
from src.api.v1.analytics import router as analytics_router
from src.api.v1.seo_workflow import router as seo_workflow_router
from src.api.v1.planning import router as planning_router
from src.api.v1.writing import router as writing_router
from src.api.v1.editing import router as editing_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"/api/v1/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(api_keys_router, prefix="/api/v1/api-keys", tags=["api-keys"])
app.include_router(keywords_router, prefix="/api/v1", tags=["keywords"])
app.include_router(seo_research_router, prefix="/api/v1", tags=["seo-research"])
app.include_router(content_router, prefix="/api/v1/content", tags=["content"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(seo_workflow_router, prefix="/api/v1", tags=["seo-workflow"])
app.include_router(planning_router, prefix="/api/v1", tags=["planning"])
app.include_router(writing_router, prefix="/api/v1", tags=["writing"])
app.include_router(editing_router, prefix="/api/v1", tags=["editing"])

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    try:
        from src.db.init_db import init_db
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        try:
            init_db(db)
            print("Database initialized successfully")
        finally:
            db.close()
    except Exception as e:
        print(f"Database initialization failed: {e}")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "SEO Agent Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Cloud Run entry point
if __name__ == "__main__":
    import os
    import uvicorn
    
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )