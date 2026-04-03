"""
Main FastAPI application entry point.
Configure and initialize the FastAPI app with database setup using Alembic migrations.
"""

import os
import subprocess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import check_db_connection
from dotenv import load_dotenv

# Import route routers
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from routes.analyze_routes import router as analyze_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "PolicyLens API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description=os.getenv("APP_DESCRIPTION", "PolicyLens Backend API"),
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route routers
app.include_router(analyze_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and run Alembic migrations on startup."""
    print("🚀 Starting PolicyLens API...")
    
    # Check database connection
    if check_db_connection():
        print("✅ Database connection successful!")
        # Run Alembic migrations
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("✅ Database migrations applied successfully!")
            else:
                print(f"⚠️  Migration warning: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Could not run migrations: {e}")
            print("    Make sure to run 'alembic upgrade head' manually")
    else:
        print("❌ Database connection failed!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 PolicyLens API shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to PolicyLens API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected" if check_db_connection() else "disconnected",
    }


@app.get("/api/debug/models")
async def list_available_models():
    """
    DEBUG ENDPOINT: List available Gemini models for your API key.
    Use this to find the correct model name to use.
    """
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}
    
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        
        available_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                available_models.append({
                    "name": m.name,
                    "display_name": m.display_name,
                    "description": m.description if hasattr(m, 'description') else None
                })
        
        return {
            "total_models": len(available_models),
            "available_for_generation": available_models
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
    )
