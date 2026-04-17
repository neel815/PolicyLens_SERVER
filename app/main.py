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
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import route routers
from routes.auth_routes import router as auth_router
from routes.policy_routes import router as policy_router
from routes.analyze_routes import router as analyze_router
from routes.simulate_routes import router as simulate_router
from routes.battle_routes import router as battle_router

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
app.include_router(auth_router, prefix="/api")
app.include_router(policy_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(simulate_router, prefix="/api")
app.include_router(battle_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database and run Alembic migrations on startup."""
    print("[STARTUP] Starting PolicyLens API...")
    
    # Check database connection
    if check_db_connection():
        print("[STARTUP] Database connection successful!")
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
                print("[STARTUP] Database migrations applied successfully!")
            else:
                print(f"[STARTUP WARNING] Migration warning: {result.stderr}")
        except Exception as e:
            print(f"[STARTUP WARNING] Could not run migrations: {e}")
            print("    Make sure to run 'alembic upgrade head' manually")
    else:
        print("[STARTUP ERROR] Database connection failed!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("[SHUTDOWN] PolicyLens API shutting down...")


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
