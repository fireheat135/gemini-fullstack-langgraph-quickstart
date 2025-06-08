"""Separate authentication FastAPI app for testing integration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a separate app for authentication testing
auth_app = FastAPI(title="SEO Agent Auth", version="1.0.0")

# Add CORS middleware
auth_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple test endpoints
@auth_app.get("/")
def auth_root():
    """Auth service root."""
    return {"message": "SEO Agent Authentication Service", "status": "running"}

@auth_app.get("/health")
def auth_health():
    """Auth service health check."""
    return {"status": "healthy", "service": "authentication"}

# Simple user endpoint for testing
@auth_app.post("/register")
def test_register():
    """Test registration endpoint."""
    return {"message": "Registration endpoint", "status": "test"}

@auth_app.post("/login")
def test_login():
    """Test login endpoint."""
    return {"message": "Login endpoint", "status": "test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(auth_app, host="0.0.0.0", port=8124)