# Alembic Migrations Guide

## Overview
Alembic is used to manage database schema changes. All database structure changes are tracked and versioned.

## Quick Start

### Apply Migrations
Run migrations to create or update database tables:
```bash
alembic upgrade head
```

### View Migration Status
Check which migrations have been applied:
```bash
alembic current
alembic history
```

## Creating New Migrations

### Option 1: Autogenerate (Recommended)
After modifying models in `app/models/`, autogenerate a migration:
```bash
# Stop the running backend first (Ctrl+C)
alembic revision --autogenerate -m "description of changes"
```

**Note**: Auto-generation works best when backend is NOT running (avoid uvicorn reloader interference).

### Option 2: Manual Migration
For complex changes or data migrations:
```bash
alembic revision -m "description"
```

Then edit the created file in `alembic/versions/` to add your SQL.

## Migration Files

Located in `alembic/versions/`:
- Each file represents a single migration
- Files are applied in order (by revision ID)
- Format: `REVISION_ID_description.py`

Example:
```python
def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        ...
    )

def downgrade() -> None:
    op.drop_table('users')
```

## Workflow

1. **Modify Model** → Add/remove columns in `app/models/`
2. **Generate Migration** → `alembic revision --autogenerate -m "..."`
3. **Review** → Edit migration file if needed
4. **Test Locally** → `alembic upgrade head`
5. **Commit** → Add migration file to git
6. **Deploy** → `alembic upgrade head` on production

## Configuration

- `alembic.ini` - Main Alembic config
- `alembic/env.py` - Database connection settings (reads `DATABASE_URL` from `.env`)

## Useful Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 001_initial

# Downgrade to previous version
alembic downgrade -1

# Show current revision
alembic current

# Show all revisions
alembic history

# Show SQL without executing
alembic upgrade head --sql

# Rollback all migrations
alembic downgrade base
```

## Troubleshooting

**Migration not detected**:
```bash
# Ensure imports are correct in alembic/env.py
# Run with verbose output
alembic upgrade head -v
```

**Revision conflicts**:
```bash
# Check for duplicate revision IDs
alembic history
```

**Database locked**:
- Ensure backend/other clients aren't connected
- Restart PostgreSQL if needed

## Initial Migration

The initial migration (`001_initial.py`) creates the `users` table. To apply it:

```bash
cd backend
alembic upgrade head
```

This replaces the old `create_db.py` script.

## Files to Delete (if present)

- ❌ `backend/create_db.py` - No longer needed with Alembic

## Initial Setup

```bash
cd backend

# Activate venv
.\venv\Scripts\activate

# Apply migrations to create tables
alembic upgrade head

# Verify tables created
python
>>> from sqlalchemy import inspect
>>> from app.db.database import engine
>>> inspect(engine).get_table_names()
['alembic_version', 'users']
```

Expected tables after initial migration:
- `alembic_version` - Tracks applied migrations
- `users` - User data table
