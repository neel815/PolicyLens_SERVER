# 🚀 Railway Environment Variables Setup

Your Railway deployment is running but needs **environment variables** configured.

## Quick Setup (2 minutes)

### Step 1: Get Your SECRET_KEY

Run this command locally to generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output:
```
AbCdEfGhIjKlMnOpQrStUvWxYz1234567890_-
```

Copy this value - you'll need it in Step 3.

### Step 2: Go to Railway Dashboard

1. Visit https://railway.app/dashboard
2. Select your PolicyLens project
3. Look for the **web** service
4. Click on the **Variables** tab

### Step 3: Add Environment Variables

In the **Variables** tab, add these variables:

#### CRITICAL (Required for app to work):
```
SECRET_KEY = [paste your generated key from Step 1]
ENV = production
DEBUG = false
```

#### RECOMMENDED (For database):
```
DATABASE_URL = [Railway will auto-fill this from PostgreSQL service]
```

#### OPTIONAL (For LLM APIs):
```
GROQ_API_KEY = [your groq api key from console.groq.com]
GOOGLE_API_KEY = [your google api key from aistudio.google.com]
CORS_ORIGINS = https://yourdomain.com
```

### Step 4: Save and Deploy

1. Click "Save Variables"
2. Railway will automatically redeploy your app
3. Check the **Logs** tab to see the deployment progress
4. Wait for "✅ Migrations completed successfully" message

---

## Full Environment Variable Reference

| Variable | Required | Example | Where to Get |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ YES | `AbCdEfGh...` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ENV` | ✅ YES | `production` | Set to `production` for Railway |
| `DEBUG` | ✅ YES | `false` | Always `false` for production |
| `DATABASE_URL` | ⚠️  Auto | `postgresql://...` | Railway PostgreSQL service auto-fills this |
| `GROQ_API_KEY` | ❌ Optional | `gsk_xxx...` | https://console.groq.com |
| `GOOGLE_API_KEY` | ❌ Optional | `AIza...` | https://aistudio.google.com |
| `CORS_ORIGINS` | ❌ Optional | `https://app.com` | Your frontend domain(s) |
| `ALGORITHM` | ❌ Optional | `HS256` | Default is `HS256` |
| `APP_NAME` | ❌ Optional | `PolicyLens API` | Default is set |
| `APP_VERSION` | ❌ Optional | `1.0.0` | Default is set |

---

## Troubleshooting

### "SECRET_KEY not set" Error
- ✅ Add `SECRET_KEY` variable in Railway Variables tab
- ✅ Make sure it's 32+ characters long
- ✅ Click "Save Variables" (don't just close the tab)

### "DATABASE_URL not set" Warning
- ⚠️ This is OK! It just means database is optional
- ✅ Database will be auto-filled by Railway PostgreSQL service
- ✅ Check if PostgreSQL service exists in your project

### "Cannot connect to database"
- ✅ Verify PostgreSQL service is running (green status)
- ✅ Check DATABASE_URL matches PostgreSQL credentials
- ✅ Migrations might not have run (check logs)

### App Still Won't Start
Check **Logs** tab:
```bash
railway logs --follow
```

Look for:
- ✅ "Starting FastAPI app" = Good
- ✅ "Migrations completed" = Database is working
- ❌ "SECRET_KEY" = Add it in Variables
- ❌ "Connection refused" = Database not ready

---

## After Setup is Complete

### Test Your API
```bash
curl https://your-railway-url.railway.app/docs
```

### Monitor Deployment
1. Go to Railway Dashboard
2. Select project → web service
3. Click **Logs** tab to see real-time logs
4. Click **Metrics** tab to see CPU/Memory usage

### Common Next Steps

1. **Update Frontend**: Set API URL in frontend deployment
2. **Connect Custom Domain**: Go to Domain settings in Railway
3. **Enable Monitoring**: Set up alerts for failures
4. **Database Backups**: Configure backup strategy

---

## Need More Help?

- **Railway Documentation**: https://railway.app/docs
- **Environment Variables Guide**: See `RAILWAY_DEPLOYMENT.md` in backend
- **Setup Checklist**: See `RAILWAY_CHECKLIST.md` in backend
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**✅ Status**: App is running but waiting for environment variables.
**Action Required**: Add SECRET_KEY and other variables in Railway dashboard.
**Time to Fix**: 2 minutes
