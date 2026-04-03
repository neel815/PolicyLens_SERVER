"""
PolicyLens Backend - Main FastAPI Application Entry Point
AI-powered insurance policy analyzer
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.analyze_routes import router as analyze_router

# Create FastAPI app instance
app = FastAPI(
    title="PolicyLens API",
    description="AI-powered insurance policy analyzer",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to PolicyLens API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
