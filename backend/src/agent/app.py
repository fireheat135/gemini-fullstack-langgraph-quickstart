# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import fastapi.exceptions

from src.agent.graph import graph as research_graph
from src.agent.seo_graph import (
    create_seo_research_graph,
    create_seo_content_graph, 
    create_seo_analysis_graph
)

# Define the FastAPI app
app = FastAPI(title="SEO Agent Platform", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost:8080",
        "https://scrib-ai-writing-superpowers-frontend-263183603168.us-west1.run.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our custom API routers
try:
    from api.v1.auth import router as auth_router
    from api.v1.users import router as users_router
    from api.v1.api_keys import router as api_keys_router
    from api.v1.keywords import router as keywords_router
    from api.v1.seo_research import router as seo_research_router
    from api.v1.content import router as content_router
    from api.v1.analytics import router as analytics_router
    from api.v1.planning import router as planning_router
    from api.v1.writing import router as writing_router
    from api.v1.editing import router as editing_router
    from api.v1.seo_workflow import router as seo_workflow_router
    
    # Include routers
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
    app.include_router(api_keys_router, prefix="/api/v1/api-keys", tags=["api-keys"])
    app.include_router(keywords_router, prefix="/api/v1", tags=["keywords"])
    app.include_router(seo_research_router, prefix="/api/v1", tags=["seo-research"])
    app.include_router(content_router, prefix="/api/v1/content", tags=["content"])
    app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(planning_router, prefix="/api/v1", tags=["planning"])
    app.include_router(writing_router, prefix="/api/v1", tags=["writing"])
    app.include_router(editing_router, prefix="/api/v1", tags=["editing"])
    app.include_router(seo_workflow_router, prefix="/api/v1", tags=["seo-workflow"])
    
    print("✅ Custom API routes loaded successfully")
except ImportError as e:
    print(f"⚠️  Some custom API routes could not be loaded: {e}")

# Create SEO workflow graphs
seo_research_graph = create_seo_research_graph()
seo_content_graph = create_seo_content_graph()
seo_analysis_graph = create_seo_analysis_graph()

# Add basic endpoints
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "SEO Agent Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "api_endpoints": "/api/v1/",
        "langgraph_endpoints": ["/assistants", "/threads", "/runs"]
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "SEO Agent Platform"}


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("🚀 Starting database initialization...")
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        # Create tables first
        from src.db.session import init_db as create_tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # Test table creation
        from src.db.session import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            print(f"📋 Created tables: {tables}")
        
        # Create sample data if no users exist
        try:
            from src.db.session import SessionLocal
            from src.db.init_db import init_db as create_sample_data
            db = SessionLocal()
            try:
                create_sample_data(db)
                print("✅ Sample data created successfully")
            finally:
                db.close()
        except Exception as sample_error:
            print(f"⚠️ Sample data creation failed (may already exist): {sample_error}")
        
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        # Continue anyway to allow the service to start


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir
    static_files_path = build_path / "assets"  # Vite uses 'assets' subdir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    build_dir = pathlib.Path(build_dir)

    react = FastAPI(openapi_url="")
    react.mount(
        "/assets", StaticFiles(directory=static_files_path), name="static_assets"
    )

    @react.get("/{path:path}")
    async def handle_catch_all(request: Request, path: str):
        fp = build_path / path
        if not fp.exists() or not fp.is_file():
            fp = build_path / "index.html"
        return fastapi.responses.FileResponse(fp)

    return react


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
