# Railway Deployment Files Summary

## Files Created for Railway Deployment

### 1. **Procfile** ⭐ CRITICAL
**Location**: `backend/Procfile`

Controls how Railway runs your application:
```
release: alembic upgrade head
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**What it does:**
- `release` phase: Runs database migrations before starting the app
- `web` phase: Starts the FastAPI server on Railway's assigned port
- Uses `$PORT` environment variable (Railway provides this)

**Why it matters:**
- Railway looks for Procfile to know how to run your app
- Ensures database is ready before app starts
- Allows Railway to manage scaling and processes

---

### 2. **railway.json** (Optional)
**Location**: `backend/railway.json`

JSON-based Railway configuration:
```json
{
  "build": { "builder": "nixpacks" },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "on_failure",
    "restartPolicyMaxRetries": 5
  }
}
```

**What it does:**
- Specifies build builder (nixpacks for Python/Node auto-detection)
- Configures number of replicas (horizontal scaling)
- Sets restart policy for reliability

**Why it matters:**
- Alternative to Procfile (use one or the other)
- More explicit configuration if needed
- Better for advanced Railway features

---

### 3. **railway.toml** (Optional)
**Location**: `backend/railway.toml`

TOML-based Railway configuration:
```toml
[build]
builder = "nixpacks"

[[services.healthchecks]]
path = "/docs"
port = "$PORT"
```

**What it does:**
- Defines health check endpoint
- Monitors app availability
- Auto-restarts if health checks fail

**Why it matters:**
- Ensures Railway knows app is running
- Automatic recovery from failures
- Better reliability and uptime

---

### 4. **.railwayignore**
**Location**: `backend/.railwayignore`

Specifies files/folders to ignore during deployment:
```
venv/
__pycache__/
.env
tests/
logs/
```

**What it does:**
- Reduces deployment size (faster builds)
- Prevents local files from being deployed
- Speeds up Docker image creation

**Why it matters:**
- Smaller deployments = faster deployments
- Prevents secrets from being exposed
- Keeps production clean

---

### 5. **RAILWAY_DEPLOYMENT.md** 📖 IMPORTANT REFERENCE
**Location**: `backend/RAILWAY_DEPLOYMENT.md`

Complete guide with:
- Step-by-step setup instructions
- Environment variable reference
- Troubleshooting guide
- Security best practices
- Scaling and monitoring tips

**Use when:**
- Setting up Railway for the first time
- Configuring environment variables
- Troubleshooting deployment issues
- Scaling your application

---

### 6. **RAILWAY_CHECKLIST.md** ✅ DEPLOYMENT CHECKLIST
**Location**: `backend/RAILWAY_CHECKLIST.md`

Pre-deployment and post-deployment checklist:
- Pre-deployment validation
- Step-by-step setup checklist
- Verification procedures
- Troubleshooting guide
- Monitoring procedures
- Security checklist

**Use when:**
- Preparing for deployment
- During deployment
- After deployment to verify success
- Regular maintenance

---

### 7. **railway_setup.py** 🔧 SETUP HELPER
**Location**: `backend/railway_setup.py`

Python script that:
- Validates project structure
- Generates secure SECRET_KEY
- Creates environment templates
- Provides deployment instructions

**How to use:**
```bash
cd backend
python railway_setup.py
```

**Output:**
- Validates Procfile, requirements.txt, app/main.py
- Generates cryptographically secure SECRET_KEY
- Creates .env.railway template
- Prints next steps

---

### 8. **.env.railway** 📝 ENVIRONMENT TEMPLATE
**Location**: `backend/.env.railway`

Template for all environment variables needed in production:
```
ENV=production
DEBUG=false
SECRET_KEY=<generated>
DATABASE_URL=<from Railway PostgreSQL>
CORS_ORIGINS=https://yourdomain.com
GROQ_API_KEY=<your key>
GOOGLE_API_KEY=<your key>
```

**Use when:**
- Configuring Railway Variables
- Understanding all configuration options
- Setting up different environments

---

## Quick Setup Guide

### 1. Install Rail CLI (Optional)
```bash
npm i -g @railway/cli
```

### 2. Generate Secret Key
```bash
python backend/railway_setup.py
```

### 3. Create Railway Project
```bash
cd backend
railway init
```

### 4. Link GitHub Repository
- Go to https://railway.app/dashboard
- Create new project → Deploy from GitHub
- Select PolicyLens repository
- Select `backend` directory

### 5. Add PostgreSQL Service
- Click "Add Service" in Railway
- Select "PostgreSQL"

### 6. Set Environment Variables
Copy from `RAILWAY_DEPLOYMENT.md` and set in Railway dashboard:
- `ENV=production`
- `DEBUG=false`
- `SECRET_KEY=<from setup.py>`
- `CORS_ORIGINS=<your domain>`
- API keys (GROQ, Google)

### 7. Deploy
```bash
git push  # Railway auto-deploys on push to main
```

Or manually:
```bash
railway up
```

### 8. Monitor
```bash
railway logs
railway status
```

---

## File Purpose Summary

| File | Purpose | Priority | Type |
|------|---------|----------|------|
| Procfile | How to run app | ⭐⭐⭐ Critical | Config |
| railway.json | Build config | ⭐⭐ Recommended | Config |
| railway.toml | Advanced config | ⭐ Optional | Config |
| .railwayignore | Ignore files | ⭐⭐ Recommended | Config |
| RAILWAY_DEPLOYMENT.md | Setup guide | ⭐⭐⭐ Critical | Docs |
| RAILWAY_CHECKLIST.md | Deployment checklist | ⭐⭐⭐ Critical | Docs |
| railway_setup.py | Setup helper script | ⭐⭐ Recommended | Script |
| .env.railway | Environment template | ⭐⭐ Recommended | Template |

---

## Next Steps

1. **Run setup script:**
   ```bash
   python backend/railway_setup.py
   ```

2. **Read deployment guide:**
   ```
   Open backend/RAILWAY_DEPLOYMENT.md
   ```

3. **Follow checklist:**
   ```
   Open backend/RAILWAY_CHECKLIST.md
   ```

4. **Go to Railway:**
   ```
   https://railway.app/dashboard
   ```

5. **Create project and connect GitHub**

6. **Add PostgreSQL service**

7. **Configure environment variables**

8. **Deploy!**

---

## Important Notes

✅ **DO:**
- Keep `.env.railway` for reference (don't commit .env)
- Use strong SECRET_KEY (32+ characters)
- Set ENV=production for production
- Use HTTPS URLs for CORS_ORIGINS
- Monitor deployment logs
- Enable health checks

❌ **DON'T:**
- Commit actual `.env` file
- Use localhost in CORS_ORIGINS
- Hardcode API keys
- Enable DEBUG in production
- Deploy without database
- Skip environment variable setup

---

## Support

- **Railway Docs**: https://railway.app/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **This Project**: Check RAILWAY_DEPLOYMENT.md

Happy deploying! 🚀
