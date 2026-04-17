# Railway Build Error Fix - Database Migration at Startup

## Problem

During Railway deployment, the build failed with:
```
sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:driver
```

This happened because Alembic was trying to run database migrations during the Docker build phase, but the DATABASE_URL environment variable wasn't available yet.

## Solution

The fix moves database migrations from the **build phase** to the **startup phase** when the database IS available:

### Files Changed:

1. **Procfile** - Now uses `python start.py` instead of uvicorn directly
2. **start.py** - New startup script that:
   - Checks if DATABASE_URL is set
   - Runs `alembic upgrade head` if database is available
   - Starts the FastAPI app
   - Gracefully handles migration failures
3. **alembic/env.py** - Updated to handle missing DATABASE_URL
4. **railway.json** - Updated startCommand to use `python start.py`
5. **railway.toml** - Updated startCommand to use `python start.py`

## How It Works

### Old Flow (Broken)
```
Build Docker Image
  ├─ Install dependencies
  └─ RUN alembic upgrade head ❌ DATABASE_URL not available!
```

### New Flow (Fixed)
```
Build Docker Image
  └─ Install dependencies ✅ (no database operations)

Start Container on Railway
  └─ python start.py
     ├─ Check if DATABASE_URL is set ✅
     ├─ Run alembic upgrade head ✅ (database is available)
     └─ Start uvicorn server ✅
```

## What Happens at Startup

When your Railway app starts:

```python
# 1. Check if database is configured
if DATABASE_URL:
    # 2. Run migrations
    alembic upgrade head
    
    # 3. Log results
    # ✅ Migrations completed successfully
else:
    # Skip migrations if no database
    # ⚠️ DATABASE_URL not set, skipping migrations
    
# 4. Start the app
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables

### Required for Production
```
ENV=production
DEBUG=false
SECRET_KEY=<your-secret-key>
DATABASE_URL=postgresql://user:pass@host:port/db  # Auto-filled by Railway PostgreSQL
```

### Optional
```
CORS_ORIGINS=https://yourdomain.com
GROQ_API_KEY=<your-api-key>
GOOGLE_API_KEY=<your-api-key>
```

## Logs During Startup

You'll see these logs in Railway:

```
INFO: Running database migrations...
INFO: ✅ Migrations completed successfully
INFO: Starting FastAPI app on port 8000...
INFO: Uvicorn running on http://0.0.0.0:8000
```

Or if database isn't available:

```
WARNING: DATABASE_URL not set, skipping migrations
INFO: Starting FastAPI app on port 8000...
INFO: Uvicorn running on http://0.0.0.0:8000
```

## Testing Locally

Before deploying to Railway, test locally:

```bash
cd backend

# Start PostgreSQL
docker-compose up -d db

# Run the startup script
python start.py
```

You should see:
```
Running database migrations...
✅ Migrations completed successfully
Starting FastAPI app on port 8000...
```

## Error Handling

The `start.py` script handles these scenarios:

| Scenario | Behavior |
|----------|----------|
| DATABASE_URL not set | Skip migrations, start app |
| Migrations fail | Log error, but continue (start app anyway) |
| App fails to start | Exit with error code 1 |
| Timeout (migrations take >5min) | Log error, continue |

This ensures your app always attempts to start, even if migrations fail.

## Rollback to Old Behavior

If you want migrations during the build (not recommended):

1. Edit Procfile:
   ```
   release: alembic upgrade head
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. Ensure DATABASE_URL is available during build (not possible with Railway)

## Railway-Specific Notes

### Why Railways Does This
- Railway's Procfile `release` phase runs AFTER services are provisioned
- But `release` phase happens during container startup, not build
- Docker build happens before services are provisioned
- So DATABASE_URL is unavailable during build

### What Actually Happens
1. Railway builds Docker image (no DATABASE_URL)
2. Railway starts container
3. Railway provisions PostgreSQL service
4. `python start.py` runs (now DATABASE_URL is available)
5. Migrations run successfully

## Monitoring

### Check Migration Status
In Railway dashboard → Logs:
```
tail -f logs/api.log | grep -i "migration\|alembic"
```

### Manual Migration
If you need to run migrations manually:
```bash
railway run alembic upgrade head
```

### Verify Database
```bash
railway run psql $DATABASE_URL -c "SELECT version();"
```

## Security Considerations

✅ **Security Benefits:**
- DATABASE_URL not exposed during build
- Secrets only used at runtime
- Docker image can be used without database
- Graceful degradation if database unavailable

❌ **Things to Avoid:**
- Don't hardcode DATABASE_URL
- Don't run migrations in Docker build
- Don't skip error logging
- Don't use plaintext passwords

## Troubleshooting

### Migrations Hang
Check Railway logs for database connectivity issues:
```
railway logs --follow
```

### Migrations Fail but App Starts
Check your migration files:
```bash
alembic current    # Show current version
alembic upgrade head --sql  # Show what will run
```

### App Won't Start
Check logs:
```
railway logs --follow
```

Common issues:
- Missing environment variables
- Database still initializing
- Connection pool exhausted
- Port already in use

### Verify Everything Works

1. Check migrations ran:
   ```
   railway run alembic current
   ```

2. Check app is healthy:
   ```
   curl https://<railway-url>/docs
   ```

3. Check logs have no errors:
   ```
   railway logs --follow --lines 50
   ```

## Questions?

Refer to:
- `RAILWAY_DEPLOYMENT.md` - Full deployment guide
- `RAILWAY_CHECKLIST.md` - Step-by-step checklist
- `start.py` - Startup script source code
- Railway Docs: https://railway.app/docs

---

**Status**: ✅ Ready for Railway Deployment
**Last Updated**: 2026-04-17
