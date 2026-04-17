#!/usr/bin/env python
"""
Startup script for Railway deployment.
Runs database migrations and then starts the FastAPI app.
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run Alembic migrations."""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.warning("DATABASE_URL not set, skipping migrations")
        return True
    
    logger.info("Running database migrations...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=False,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Migrations completed successfully")
            return True
        else:
            logger.error(f"❌ Migrations failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Migrations timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"❌ Error running migrations: {e}")
        return False


def start_app():
    """Start the FastAPI application."""
    port = os.getenv("PORT", "8000")
    logger.info(f"Starting FastAPI app on port {port}...")
    
    try:
        subprocess.run(
            [
                "uvicorn",
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", port,
            ],
            check=True
        )
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error starting app: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run migrations first
    if not run_migrations():
        logger.warning("⚠️  Migrations had issues, continuing anyway...")
    
    # Start the app
    start_app()
