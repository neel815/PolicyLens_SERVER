# PolicyLens Backend API

FastAPI backend for PolicyLens project with PostgreSQL database integration.

## Project Structure

```
backend/
├── app/
│   ├── db/
│   │   ├── database.py         # Database connection & session management
│   │   └── __init__.py
│   ├── models/
│   │   ├── base.py             # Base model with common fields
│   │   ├── user.py             # Example User model
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── user.py             # Pydantic schemas for validation
│   │   └── __init__.py
│   ├── routes/
│   │   ├── user.py             # Example API endpoints
│   │   └── __init__.py
│   ├── services/               # Business logic layer
│   ├── config/                 # App configuration
│   ├── utils/                  # Helper functions
│   ├── middleware/             # Custom middleware
│   ├── main.py                 # FastAPI app initialization
│   └── __init__.py
├── tests/                      # Test suite
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment file
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Setup Instructions

### 1. Create PostgreSQL Database

```sql
CREATE DATABASE policylens;
```

### 2. Install Dependencies

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update if needed:
```bash
cp .env.example .env
```

Default values in `.env`:
- Database: `policylens`
- User: `postgres`
- Password: `root@123`
- Host: `127.0.0.1:5432`

### 4. Run the Application

```bash
python -m app.main

# Or use uvicorn directly:
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## Database Connection

The database module (`app/db/database.py`) provides:

### `get_db()` - Dependency Injection
Use in routes for automatic session management:
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

### `get_db_context()` - Context Manager
Use for standalone scripts:
```python
from app.db import get_db_context

with get_db_context() as db:
    users = db.query(User).all()
```

### `init_db()` - Create Tables
```python
from app.db import init_db
init_db()  # Creates all tables from models
```

### `check_db_connection()` - Test Connection
```python
from app.db import check_db_connection
if check_db_connection():
    print("Connected!")
```

## Creating Models

All models inherit from `BaseModel` which provides:
- `id` (Primary Key)
- `created_at` (Auto-timestamp)
- `updated_at` (Auto-timestamp)

Example model in `app/models/`:
```python
from sqlalchemy import Column, String
from app.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"
    
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
```

## API Routes

Example routes in `app/routes/user.py`:
- `POST /api/users/` - Create user
- `GET /api/users/{user_id}` - Get user
- `GET /api/users/` - List users
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

## Testing

Run tests with pytest:
```bash
pytest
pytest -v  # Verbose
pytest --cov  # With coverage
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ENV | development | App environment |
| DEBUG | true | Debug mode |
| DATABASE_URL | postgresql://postgres:root%40123@127.0.0.1:5432/policylens | DB connection string |
| SERVER_HOST | 0.0.0.0 | Server host |
| SERVER_PORT | 8000 | Server port |
| CORS_ORIGINS | http://localhost:3000 | Allowed CORS origins |

## Common Tasks

### Add a New Model
1. Create in `app/models/your_model.py`
2. Import in `app/models/__init__.py`
3. Models auto-create on app startup

### Add New Routes
1. Create in `app/routes/your_routes.py`
2. Import and include in `app/main.py`:
```python
from app.routes import your_routes
app.include_router(your_routes.router)
```

### Database Migrations
Use Alembic for schema changes:
```bash
alembic init .
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Troubleshooting

**Connection Error**: Check DATABASE_URL and ensure PostgreSQL is running
```bash
psql -U postgres -h 127.0.0.1 -d policylens
```

**Import Error**: Ensure backend directory is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

**Port Already in Use**: Change SERVER_PORT in `.env`

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
