This folder contains Alembic migration scripts.

- Use `alembic revision --autogenerate -m "message"` to create a new migration.
- Use `alembic upgrade head` to apply migrations.

Alembic is configured to read `DATABASE_URL` from the backend `.env` file.