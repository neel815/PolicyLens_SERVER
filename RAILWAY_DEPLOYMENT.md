# Railway Deployment Guide for PolicyLens Backend

## Prerequisites
1. Railway account (https://railway.app)
2. GitHub repository with the PolicyLens code
3. PostgreSQL database (Railway provides one)

## Step 1: Connect GitHub Repository

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Authorize Railway to access your GitHub account
5. Select the PolicyLens repository
6. Select the `backend` directory as the root

## Step 2: Add PostgreSQL Database

1. In your Railway project, click "Add Service"
2. Select "PostgreSQL"
3. Railway will automatically provision a PostgreSQL database
4. Note the `DATABASE_URL` - you'll need it in Step 3

## Step 3: Configure Environment Variables

In Railway project dashboard, go to **Variables** and add these environment variables:

### Required Variables
```
ENV=production
DEBUG=false

# Replace with your actual values
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALGORITHM=HS256

# Database URL (from PostgreSQL service)
DATABASE_URL=<auto-filled by Railway from PostgreSQL service>

# CORS Origins (set to your frontend domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# API Configuration
APP_NAME=PolicyLens API
APP_VERSION=1.0.0
APP_DESCRIPTION=PolicyLens Backend API

# LLM API Keys
GROQ_API_KEY=<your groq api key>
GOOGLE_API_KEY=<your google gemini api key>

# Database Connection Pooling (optional, for high traffic)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_RECYCLE=3600
```

## Step 4: Database Migrations

Railway will automatically run the `release` command in Procfile:
```
alembic upgrade head
```

This runs database migrations before starting the app.

## Step 5: Deploy

1. Push your code to GitHub
2. Railway will automatically detect changes and redeploy
3. Check deployment logs in the Railway dashboard

## Step 6: Get Your API URL

After successful deployment:
1. Go to Railway project dashboard
2. Click on the `web` service
3. Under "Domain", you'll see your API URL (e.g., `https://policylens-prod-abc123.railway.app`)
4. Update your frontend `next.config.ts` to use this URL:

```typescript
export default {
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: '/api/:path*',
          destination: 'https://policylens-prod-abc123.railway.app/api/:path*',
        },
      ],
    };
  },
};
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `ENV` | Environment type | `production` |
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | JWT signing key (32+ chars) | Generated |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `CORS_ORIGINS` | Allowed frontend domains | `https://yourdomain.com` |
| `GROQ_API_KEY` | Groq API key for LLM | Your API key |
| `GOOGLE_API_KEY` | Google Gemini API key | Your API key |
| `APP_NAME` | API name | `PolicyLens API` |
| `APP_VERSION` | API version | `1.0.0` |
| `DB_POOL_SIZE` | Database connection pool size | `20` |
| `DB_MAX_OVERFLOW` | Database overflow connections | `40` |

## Monitoring & Logs

1. Go to Railway dashboard → Your Project → web service
2. Click on **Logs** tab to see real-time application logs
3. Click on **Metrics** tab to see CPU, memory, and request metrics

## Troubleshooting

### Database Connection Error
- Verify `DATABASE_URL` is set correctly
- Check that PostgreSQL service is running (green status in Railway)
- Run migrations manually: `alembic upgrade head`

### CORS Errors
- Update `CORS_ORIGINS` to include your frontend domain
- Ensure no `localhost` in production environment

### API Keys Not Working
- Verify `GROQ_API_KEY` and `GOOGLE_API_KEY` are set
- Check that API keys have correct permissions
- Regenerate keys if necessary

### Port Issues
- Railway automatically assigns a port via `$PORT` environment variable
- Procfile must use `$PORT` for the app port
- Do not hardcode ports (3000, 8000, etc.)

## Rolling Back

If deployment fails:
1. Go to Railway dashboard
2. Click on **Deployments**
3. Select the previous successful deployment
4. Click **Redeploy**

## Scaling

To scale your application:
1. Go to Railway project → web service
2. Click **Settings**
3. Increase **Num Replicas** for horizontal scaling
4. Adjust **Memory** and **CPU** for vertical scaling

## Security Best Practices

✅ **DO:**
- Use strong `SECRET_KEY` (32+ characters)
- Never commit `.env` files
- Use environment variables for all secrets
- Enable debug only in development
- Restrict CORS to specific domains

❌ **DON'T:**
- Use `localhost` in production CORS_ORIGINS
- Hardcode API keys
- Enable DEBUG in production
- Use default database credentials
- Expose `/docs` endpoint in production

## Support

For Railway issues: https://railway.app/docs
For PolicyLens issues: Check GitHub issues or reach out to the team
