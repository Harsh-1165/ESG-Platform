# Render.com Deployment Guide

Step-by-step instructions for deploying to Render.com

---

## Prerequisites

1. GitHub account with code pushed to a public or private repository
2. Render account (free tier available: https://render.com)
3. Your domain name (or use free Render domain)

---

## Step 1: Connect GitHub to Render

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Connect a repository"**
4. Authorize Render to access your GitHub account
5. Select your repository
6. Click **"Connect"**

---

## Step 2: Configure Backend Service

### 2.1 Basic Settings

| Setting | Value |
|---------|-------|
| **Name** | `esg-backend-prod` |
| **Environment** | Python 3 |
| **Region** | Select closest to your users |
| **Branch** | `main` |

### 2.2 Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn config.wsgi -w 4 -b 0.0.0.0:10000
```

### 2.3 Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `esg-postgres-prod`
3. Database: `esg_db`
4. Copy the connection string (you'll need this for environment variables)

---

## Step 3: Set Environment Variables

Click **"Environment"** in your web service settings and add each variable:

### Required Variables

```
DEBUG=False
SECRET_KEY=[generate new one]
ENVIRONMENT=production
ALLOWED_HOSTS=your-backend-domain.onrender.com
```

### Database Variables

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=esg_db
DB_USER=postgres
DB_PASSWORD=[from render postgres]
DB_HOST=[from render postgres host]
DB_PORT=5432
```

### CORS & Security

```
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
```

### Generate SECRET_KEY Locally (IMPORTANT!)

Never use your development SECRET_KEY in production. Generate a new one:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output to `SECRET_KEY` in Render environment variables.

---

## Step 4: Deploy Backend

1. Click **"Create Web Service"** or **"Deploy"** if redeploying
2. Wait for the build to complete (5-10 minutes)
3. Check the logs for any errors
4. Get the backend URL (e.g., `https://esg-backend-prod.onrender.com`)

### Test Backend

```bash
# Verify API is responding
curl -I https://your-backend-domain.onrender.com/api/

# Should return 403 Forbidden (requires auth) or 400 Bad Request
# NOT 500 error
```

If you get a 500 error:
1. Check Render logs for error messages
2. Verify all environment variables are set correctly
3. Check database connection

---

## Step 5: Deploy Frontend

### Option 1: Using Render Static Site (Recommended)

1. Click **"New +"** → **"Static Site"**
2. Select your GitHub repository
3. Configure as follows:

| Setting | Value |
|---------|-------|
| **Name** | `esg-frontend-prod` |
| **Branch** | `main` |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Publish Directory** | `frontend/build` |

### Environment Variables

```
REACT_APP_API_URL=https://your-backend-domain.com/api
REACT_APP_APP_NAME=ESG Platform
```

### Deploy

1. Click **"Create Static Site"**
2. Wait for build to complete
3. Get the frontend URL (e.g., `https://esg-frontend-prod.onrender.com`)

---

## Step 6: Update Backend CORS Settings

Now that your frontend is deployed, update the backend:

1. Go to backend service in Render
2. Update environment variables:
   ```
   CORS_ALLOWED_ORIGINS=https://esg-frontend-prod.onrender.com
   CSRF_TRUSTED_ORIGINS=https://esg-frontend-prod.onrender.com
   ```
3. Click **"Deploy"** to redeploy with new settings

---

## Step 7: Test the Full Application

1. Visit your frontend domain: `https://esg-frontend-prod.onrender.com`
2. Verify the page loads
3. Try to upload data or access an API endpoint
4. Check for any CORS errors in browser console

---

## Step 8: Set Up Custom Domain (Optional)

### For Backend (If you have a custom domain)

1. Go to backend service → **"Settings"**
2. Scroll to **"Custom Domains"**
3. Add your domain (e.g., `api.your-domain.com`)
4. Follow DNS instructions from Render
5. Update `ALLOWED_HOSTS` environment variable
6. Redeploy

### For Frontend

1. Go to frontend service → **"Settings"**
2. Scroll to **"Custom Domains"**
3. Add your domain (e.g., `www.your-domain.com`)
4. Update `CORS_ALLOWED_ORIGINS` on backend
5. Redeploy both services

---

## Step 9: Enable Auto-Deployment

Configure auto-deployment so every push to `main` automatically deploys:

1. In service → **"Settings"** → **"Auto-Deploy"**
2. Select **"Yes"** for both services
3. Now every git push triggers a new deployment

---

## Step 10: Database Backups

### Enable Automatic Backups

1. Go to PostgreSQL instance → **"Settings"**
2. Enable **"Automated Backups"**
3. Set retention to 30+ days

### Manual Backup

```bash
# Export database (run locally)
pg_dump -U postgres -h your-render-host -d esg_db > backup.sql
```

### Restore from Backup

Contact Render support or restore via:
```bash
psql -U postgres -h your-render-host -d esg_db < backup.sql
```

---

## Step 11: Monitoring & Alerts

### Enable Notifications

1. Render dashboard → **"Notifications"** or **"Settings"**
2. Add email for deployment failures
3. Add alerts for service crashes

### Check Logs

1. Service → **"Logs"** tab
2. Filter by date/time
3. Look for `ERROR` or `CRITICAL` messages

### Common Issues in Logs

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Missing dependency in `requirements.txt` |
| `ALLOWED_HOSTS` validation | Update environment variable |
| `CORS error` | Update `CORS_ALLOWED_ORIGINS` |
| `Database connection refused` | Check `DB_HOST`, `DB_PASSWORD` |
| `No migrations found` | Run `python manage.py migrate` in build |

---

## Step 12: Scaling & Performance

### For Light Traffic (Free Tier OK)

- Plan: Starter ($7/month) or free tier for testing
- Workers: 4 (already set in start command)
- No additional scaling needed

### For Production (200+ req/sec)

1. Upgrade to **Pro** or **Standard** plan
2. Increase workers: `gunicorn config.wsgi -w 8 -b 0.0.0.0:10000`
3. Add caching layer (Redis on Render)
4. Add CDN for static files (Cloudflare free tier)

---

## Troubleshooting

### Issue: "Application failed to start"

**Check**:
1. Build log shows all dependencies installed
2. Migrations completed successfully
3. All required environment variables are set

```bash
# SSH into service and check
render logs [service-id]
```

### Issue: "Frontend can't reach backend"

**Check**:
1. `REACT_APP_API_URL` is correct
2. Backend `CORS_ALLOWED_ORIGINS` includes frontend domain
3. No typos in environment variables

```javascript
// In browser console, check:
console.log(process.env.REACT_APP_API_URL);
// Should print your backend URL
```

### Issue: "Database connection timeout"

**Check**:
1. Render PostgreSQL instance is running
2. `DB_HOST` and `DB_PASSWORD` are correct
3. Network connectivity (Render auto-allows)

```bash
# Test connection locally:
psql -U postgres -h your-host -d esg_db
```

### Issue: "502 Bad Gateway"

Backend crashed:
1. Check Render logs for Python errors
2. Verify `gunicorn` command in start command
3. Ensure database is accessible

---

## Cost Estimate (Monthly)

| Service | Free | Paid |
|---------|------|------|
| Web Service (Backend) | N/A | ~$7 |
| Static Site (Frontend) | Free | N/A |
| PostgreSQL | N/A | ~$15 |
| **Total** | **Free** | **~$22** |

---

## Next Steps

1. ✅ Deploy backend and frontend
2. ✅ Test all API endpoints
3. ✅ Enable database backups
4. ✅ Set up monitoring
5. 📧 Add custom domain
6. 🎯 Create Render alerts
7. 📈 Monitor performance

---

**Deployment complete!** Your application is now live on Render.
