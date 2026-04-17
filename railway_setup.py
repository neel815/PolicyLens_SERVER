#!/usr/bin/env python3
"""
Railway Deployment Setup Helper

This script helps prepare your application for Railway deployment by:
1. Generating secure SECRET_KEY
2. Validating environment configuration
3. Creating .env.railway template
"""

import os
import sys
import secrets
from pathlib import Path


def generate_secret_key(length: int = 32) -> str:
    """Generate a cryptographically secure secret key."""
    return secrets.token_urlsafe(length)


def validate_requirements() -> bool:
    """Check if requirements.txt exists."""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt not found!")
        return False
    print("✅ requirements.txt found")
    return True


def validate_procfile() -> bool:
    """Check if Procfile exists."""
    procfile = Path("Procfile")
    if not procfile.exists():
        print("❌ Procfile not found!")
        return False
    print("✅ Procfile found")
    return True


def validate_app_main() -> bool:
    """Check if app/main.py exists."""
    main = Path("app/main.py")
    if not main.exists():
        print("❌ app/main.py not found!")
        return False
    print("✅ app/main.py found")
    return True


def validate_alembic() -> bool:
    """Check if alembic is configured."""
    alembic_ini = Path("alembic.ini")
    alembic_dir = Path("alembic")
    
    if not alembic_ini.exists() or not alembic_dir.exists():
        print("❌ Alembic not configured!")
        return False
    print("✅ Alembic configured")
    return True


def create_railway_env_template() -> None:
    """Create a template .env.railway file."""
    template = f"""# ============================================================================
# RAILWAY DEPLOYMENT ENVIRONMENT TEMPLATE
# Copy values from here to Railway dashboard Variables
# ============================================================================

# Application Environment
ENV=production
DEBUG=false

# ============================================================================
# SECURITY - CRITICAL FOR PRODUCTION
# ============================================================================

# Generated Secret Key (copy from Railway_SETUP_OUTPUT below)
SECRET_KEY={generate_secret_key()}

# JWT Algorithm
ALGORITHM=HS256

# ============================================================================
# DATABASE CONFIGURATION
# Railway will auto-provide DATABASE_URL from PostgreSQL service
# DO NOT set DATABASE_URL here - Railway handles it automatically
# ============================================================================

# These are for reference only:
# DATABASE_URL will be injected by Railway PostgreSQL plugin
# Format: postgresql://user:password@host:port/database

# Database Connection Pooling (optional)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_RECYCLE=3600

# ============================================================================
# CORS CONFIGURATION
# Replace with your actual frontend domain(s)
# ============================================================================
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ============================================================================
# LLM API KEYS
# Get these from:
# - Groq: https://console.groq.com
# - Google: https://aistudio.google.com
# ============================================================================
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxxx

# ============================================================================
# API CONFIGURATION
# ============================================================================
APP_NAME=PolicyLens API
APP_VERSION=1.0.0
APP_DESCRIPTION=PolicyLens Backend API - Insurance Policy Analysis Platform

# ============================================================================
# LOGGING CONFIGURATION (optional)
# ============================================================================
LOG_LEVEL=INFO

# ============================================================================
# RATE LIMITING CONFIGURATION (optional)
# ============================================================================
RATE_LIMIT_ENABLED=true
"""
    
    with open(".env.railway", "w") as f:
        f.write(template)
    print("✅ Created .env.railway template")


def print_setup_instructions() -> None:
    """Print Railway setup instructions."""
    secret_key = generate_secret_key()
    
    print("\n" + "=" * 80)
    print("RAILWAY DEPLOYMENT SETUP")
    print("=" * 80)
    
    print("\n📋 FILES CREATED:")
    print("  ✅ Procfile - Process configuration")
    print("  ✅ railway.json - Railway build config")
    print("  ✅ railway.toml - Alternative Railway config")
    print("  ✅ .env.railway - Environment template")
    print("  ✅ RAILWAY_DEPLOYMENT.md - Complete guide")
    
    print("\n🔐 GENERATED SECRET KEY (copy to Railway):")
    print(f"  {secret_key}")
    
    print("\n📝 NEXT STEPS:")
    print("  1. Go to https://railway.app/dashboard")
    print("  2. Create new project and connect GitHub")
    print("  3. Select backend directory as root")
    print("  4. Add PostgreSQL service")
    print("  5. Set these environment variables in Railway:")
    print(f"     - SECRET_KEY={secret_key}")
    print("     - ENV=production")
    print("     - DEBUG=false")
    print("     - CORS_ORIGINS=https://yourdomain.com")
    print("     - GROQ_API_KEY=your_groq_key")
    print("     - GOOGLE_API_KEY=your_google_key")
    print("  6. DATABASE_URL will be auto-filled by Railway PostgreSQL service")
    print("  7. Deploy!")
    
    print("\n📚 DOCUMENTATION:")
    print("  - Read RAILWAY_DEPLOYMENT.md for detailed guide")
    print("  - Read .env.railway for all configuration options")
    print("  - Full Railway docs: https://railway.app/docs")
    
    print("\n✅ Setup complete! Your backend is ready for Railway deployment.")
    print("=" * 80 + "\n")


def main() -> int:
    """Run setup validation and create files."""
    print("🚀 Railway Deployment Setup Helper\n")
    
    # Validate existing files
    print("🔍 Validating project structure...")
    checks = [
        validate_requirements(),
        validate_procfile(),
        validate_app_main(),
        validate_alembic(),
    ]
    
    if not all(checks):
        print("\n❌ Some required files are missing!")
        return 1
    
    print("\n📝 Creating configuration files...")
    try:
        create_railway_env_template()
    except Exception as e:
        print(f"❌ Error creating templates: {e}")
        return 1
    
    # Print setup instructions
    print_setup_instructions()
    return 0


if __name__ == "__main__":
    sys.exit(main())
