#!/usr/bin/env python
"""Verify that Alembic migrations created the tables successfully."""

from sqlalchemy import inspect
from app.db.database import engine

try:
    ins = inspect(engine)
    tables = ins.get_table_names()
    
    print("✅ MIGRATION VERIFICATION")
    print(f"   Tables created: {tables}")
    
    if 'users' in tables:
        print("\n📋 Users table columns:")
        for col in ins.get_columns('users'):
            print(f"   - {col['name']}: {col['type']}")
        print("\n✅ Database schema ready!")
    else:
        print("\n❌ Users table not found!")
        
except Exception as e:
    print(f"❌ Error: {e}")
