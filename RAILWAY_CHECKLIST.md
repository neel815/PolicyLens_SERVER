# Railway Quick Start Checklist

## Pre-Deployment Checklist

- [ ] Railway account created (https://railway.app)
- [ ] GitHub repository is public or Railway has access
- [ ] All environment variables defined in requirements
- [ ] Database migrations (alembic) are up to date
- [ ] `.env` file is NOT committed to git (check .gitignore)
- [ ] `requirements.txt` includes all dependencies
- [ ] Procfile is in the backend root directory
- [ ] `app/main.py` exists and is the entry point

## Railway Setup Steps

### Step 1: Create Railway Project
- [ ] Go to https://railway.app/dashboard
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub"
- [ ] Authorize Railway to access GitHub
- [ ] Select PolicyLens repository
- [ ] Select `backend` directory as root

### Step 2: Add PostgreSQL Database
- [ ] In Railway project, click "Add Service"
- [ ] Select "PostgreSQL"
- [ ] Wait for database to be provisioned
- [ ] Copy `DATABASE_URL` from variables

### Step 3: Configure Environment Variables
Add these to Railway project Variables:

```
ENV=production
DEBUG=false
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALGORITHM=HS256
CORS_ORIGINS=https://yourdomain.com
GROQ_API_KEY=<your API key>
GOOGLE_API_KEY=<your API key>
APP_NAME=PolicyLens API
APP_VERSION=1.0.0
APP_DESCRIPTION=PolicyLens Backend API
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_RECYCLE=3600
```

- [ ] All critical variables set (ENV, DEBUG, SECRET_KEY, CORS_ORIGINS)
- [ ] API keys configured (GROQ, Google)
- [ ] DATABASE_URL is auto-filled from PostgreSQL service
- [ ] CORS_ORIGINS points to production frontend domain

### Step 4: Deploy & Test
- [ ] Verify Procfile exists in backend root
- [ ] Commit and push code to GitHub
- [ ] Railway automatically triggers deployment
- [ ] Monitor deployment in Railway dashboard → Deployments
- [ ] Check logs in Railway dashboard → Logs tab
- [ ] Wait for "Build successful" message

### Step 5: Verify Deployment
- [ ] Get API URL from Railway dashboard (Domain section)
- [ ] Test health check: `curl https://<railway-url>/docs`
- [ ] Test CSRF endpoint: `curl -X POST https://<railway-url>/api/csrf-token`
- [ ] Test auth endpoint: `curl -X POST https://<railway-url>/api/auth/register`
- [ ] Check logs for errors

### Step 6: Update Frontend
- [ ] Update frontend `next.config.ts` with Railway API URL
- [ ] Or update environment variable in frontend deployment
- [ ] Test API integration from frontend

## Important Configuration Files

### Procfile
```
release: alembic upgrade head
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
- ✅ Runs migrations before deployment
- ✅ Starts app on Railway-assigned port
- ✅ Uses correct ASGI server

### railway.json
```json
{
  "build": { "builder": "nixpacks" },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```
- ✅ Defines build strategy
- ✅ Configures deployment settings

### requirements.txt
- [ ] Contains all dependencies
- [ ] Includes FastAPI, uvicorn, psycopg2, sqlalchemy, etc.
- [ ] No dev dependencies needed (pytest, black, etc. can be removed)

## Troubleshooting

### Deployment Fails
- [ ] Check Railway deployment logs
- [ ] Verify Procfile exists and is correct
- [ ] Check requirements.txt has all dependencies
- [ ] Verify Python version (3.9+)

### Database Connection Error
- [ ] Verify DATABASE_URL in Railway Variables
- [ ] Check PostgreSQL service is running (green status)
- [ ] Run migrations: Check logs for alembic errors
- [ ] Verify DB credentials in URL

### CORS Errors in Frontend
- [ ] Update CORS_ORIGINS in Railway Variables
- [ ] Restart deployment after changing CORS_ORIGINS
- [ ] Ensure no `localhost` in production CORS_ORIGINS

### API Returns 500 Errors
- [ ] Check logs in Railway dashboard
- [ ] Verify all required environment variables are set
- [ ] Check API keys (GROQ, Google) are valid
- [ ] Verify database migrations ran successfully

### Slow Response Times
- [ ] Monitor metrics in Railway dashboard
- [ ] Increase CPU/Memory if needed
- [ ] Check database connection pool settings
- [ ] Monitor API rate limits

## Monitoring & Maintenance

### Daily Monitoring
- [ ] Check Railway dashboard for deployment status
- [ ] Review error logs (Railway → Logs)
- [ ] Monitor resource usage (CPU, Memory, Database)
- [ ] Verify API is responding

### Weekly Maintenance
- [ ] Review application logs for warnings
- [ ] Check database performance
- [ ] Verify CORS_ORIGINS are still correct
- [ ] Test critical API endpoints

### Monthly Updates
- [ ] Update dependencies in requirements.txt
- [ ] Review security logs
- [ ] Test backup/recovery procedures
- [ ] Review database usage and scaling needs

## Rollback Plan

If deployment has issues:
1. Go to Railway dashboard → Deployments
2. Click on previous successful deployment
3. Click "Redeploy"
4. Monitor new deployment logs

## Scaling (When Needed)

### Horizontal Scaling
- Railway dashboard → web service → Settings
- Increase "Num Replicas"
- Restarts with multiple instances

### Vertical Scaling
- Railway dashboard → web service → Settings
- Increase "Memory" and "CPU"
- Requires restart

### Database Scaling
- Railway dashboard → PostgreSQL service → Settings
- Increase storage/CPU
- Monitor connections and query performance

## Cost Optimization

- Use Railway's free tier if possible
- Monitor usage metrics
- Clean up old deployments
- Use connection pooling
- Enable caching where applicable

## Security Checklist

- [ ] SECRET_KEY is 32+ characters
- [ ] DEBUG=false in production
- [ ] No localhost in CORS_ORIGINS
- [ ] API keys are secret (not in code)
- [ ] Database password is strong
- [ ] Use HTTPS only (Railway provides this)
- [ ] Enable rate limiting (configured in backend)
- [ ] Validate all user inputs (Pydantic handles this)

## Support & Resources

- **Railway Docs**: https://railway.app/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs
- **PolicyLens GitHub**: Check GitHub issues
- **Railway Support**: https://railway.app/docs/support

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Notes**: _______________
