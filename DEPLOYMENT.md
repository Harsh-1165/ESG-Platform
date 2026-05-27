# Deployment Guide for ESG Platform

Comprehensive guide for deploying this Django + React application to production (Render.com).

---

## Part 1: Production Readiness Checklist

### Backend Configuration

- [ ] **DEBUG = False** (only in production, never True)
- [ ] **SECRET_KEY** generated and stored securely (not in code)
- [ ] **ALLOWED_HOSTS** set correctlly (your domain)
- [ ] **Database** uses PostgreSQL (not SQLite)
- [ ] **CORS_ALLOWED_ORIGINS** points to frontend domain
- [ ] **Static files** configured for serving (WhiteNoise or similar)
- [ ] **CSRF** properly configured (CSRF_TRUSTED_ORIGINS)
- [ ] **SSL/TLS** enabled (HTTPS)
- [ ] **Security headers** set (HSTS, etc.)
- [ ] **Email backend** configured for password resets
- [ ] **Logging** configured for monitoring
- [ ] **Environment variables** all set in production system

### Frontend Configuration

- [ ] **API_URL** points to production backend
- [ ] **Auth tokens** cleared before production build
- [ ] **Build optimized** (ran `npm run build`)
- [ ] **Static files** minified and hashed
- [ ] **Environment variables** set correctly
- [ ] **Error logging** enabled (optional but recommended)

### Database

- [ ] **PostgreSQL** running and accessible
- [ ] **Database user** has limited permissions
- [ ] **Migrations** applied to production database
- [ ] **Backups** configured
- [ ] **Production password** different from development

### Security

- [ ] **Secrets** stored in environment variables (not `.env` files in production)
- [ ] **API keys** rotated and secured
- [ ] **Rate limiting** configured (optional but recommended)
- [ ] **Input validation** on all endpoints
- [ ] **SQL injection** prevention (using Django ORM)
- [ ] **CSRF protection** enabled

---

## Part 2: Environment Variables

### Backend (.env file - Development only)

```bash
# Django Settings
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=esg_prototype
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# CORS & Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional Monitoring
SENTRY_DSN=
LOG_LEVEL=INFO
```

### Frontend (.env file - Development only)

```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_APP_NAME=ESG Platform
```

### Production Environment Variables (set in Render.com dashboard)

**Backend:**
```
DEBUG=False
SECRET_KEY=[generate with Django]
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-app.onrender.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres_user
DB_PASSWORD=[strong password]
DB_HOST=[render postgres host]
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com:.https://www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
ALLOWED_HOSTS=your-domain.onrender.com
```

**Frontend:**
```
REACT_APP_API_URL=https://your-api-domain.com/api
```

---

## Part 3: CORS Configuration

### Current Settings (Development)

```python
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True
```

### Production Settings

Update `backend/config/settings.py`:

```python
# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://your-domain.com'
).split(',')

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

---

## Part 4: Static Files Setup

### Django Static Files Configuration

Update `backend/config/settings.py`:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')

# Whitenoise for serving static files in production
# Add 'whitenoise.middleware.WhiteNoiseMiddleware' early in MIDDLEWARE
```

### Step-by-Step Setup

1. **Install WhiteNoise** (for production static file serving):
   ```bash
   pip install whitenoise==6.6.0
   ```

2. **Update `requirements.txt`**:
   ```bash
   pip freeze > requirements.txt
   ```

3. **Update MIDDLEWARE** in `settings.py`:
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
       'corsheaders.middleware.CorsMiddleware',
       # ... rest of middleware
   ]
   ```

4. **Configure static files**:
   ```python
   STATIC_URL = '/static/'
   STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
   ```

5. **Collect static files** (run before deployment):
   ```bash
   python manage.py collectstatic --noinput
   ```

---

## Part 5: Database Configuration

### PostgreSQL Setup for Production

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### Migration Strategy

1. **In development**, test all migrations locally:
   ```bash
   python manage.py makemigrations
   python manage.py migrate --plan  # preview changes
   python manage.py migrate
   ```

2. **Before production deployment**, run:
   ```bash
   python manage.py migrate --noinput
   ```

3. **Always backup production database before migrations**:
   ```bash
   # Using pg_dump
   pg_dump -U postgres -h your-host esg_prototype > backup.sql
   ```

---

## Part 6: Frontend Build Commands

### Development Build

```bash
cd frontend
npm install
npm start
```

### Production Build

```bash
# Build optimized production bundle
cd frontend
npm install
npm run build

# Output goes to: frontend/build/
# Size should be < 100KB gzipped for main.js
```

### Testing Production Build Locally

```bash
# Install serve
npm install -g serve

# Serve the production build
serve -s build -p 3000
```

---

## Part 7: Deployment Checklist for Render.com

### Pre-Deployment Checklist

- [ ] All code committed and pushed to GitHub
- [ ] Branch protection rules in place (require PR reviews)
- [ ] Secrets not in code (all in environment variables)
- [ ] Database backups configured
- [ ] Frontend build tested locally (`npm run build`)
- [ ] All migrations tested in development
- [ ] Error logs/monitoring setup (Sentry, etc.)

### Render Deployment Steps

#### 1. Backend Deployment

1. **Create New Web Service in Render**
   - Name: `esg-backend-prod`
   - GitHub repo: Select your repo
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn config.wsgi -w 4 -b 0.0.0.0:10000`

2. **Add PostgreSQL Database**
   - Create a new PostgreSQL instance
   - Copy connection details to environment variables

3. **Set Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=[generate a new one]
   ALLOWED_HOSTS=your-backend-domain.onrender.com
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=esg_db
   DB_USER=postgres
   DB_PASSWORD=[from render postgres]
   DB_HOST=[render postgres host]
   DB_PORT=5432
   CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
   CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

4. **Deploy and verify**
   - Check logs: `curl https://your-backend-domain.onrender.com/api/`
   - Should return 403 (requires auth) or 404, NOT 500 error

#### 2. Frontend Deployment

**Option A: Render Static Site**

1. **Create Static Site in Render**
   - Name: `esg-frontend-prod`
   - GitHub repo: Select your repo
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/build`

2. **Set Environment Variables**
   ```
   REACT_APP_API_URL=https://your-backend-domain.onrender.com/api
   ```

3. **Add custom domain** if you have one

**Option B: Deploy Together (Monorepo approach)**

Use a single Render service with a custom start script (more complex, not recommended for beginners).

---

## Part 8: Common Deployment Errors & Solutions

### Error 1: ModuleNotFoundError: No module named 'X'

**Cause**: Missing dependency
```bash
# Solution:
pip install [missing-module]
pip freeze > requirements.txt
# Commit and redeploy
```

### Error 2: ALLOWED_HOSTS validation failed

**Cause**: Django doesn't recognize the deployment domain
```python
# Solution in settings.py:
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost'
).split(',')

# Set in Render:
ALLOWED_HOSTS=your-domain.onrender.com,your-custom-domain.com
```

### Error 3: CORS errors (404 for OPTIONS requests)

**Cause**: CORS path not included in URL config
```python
# Ensure this is in settings.py:
INSTALLED_APPS = [
    # ...
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Must be early
    # ...
]
```

### Error 4: Static files returning 404

**Cause**: WhiteNoise not installed or misconfigured
```bash
# Solution:
pip install whitenoise
pip freeze > requirements.txt

# In settings.py:
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add here
    # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Error 5: Database connection timeout

**Cause**: Render PostgreSQL not accessible
```python
# In settings.py, add connection pooling:
DATABASES = {
    'default': {
        # ...
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### Error 6: Frontend API calls return 403/CORS errors

**Check**:
1. `CORS_ALLOWED_ORIGINS` includes frontend domain
2. Frontend sends `Authorization: Token XXX` header
3. Request path matches Django URL patterns

```javascript
// In frontend/src/api/client.js:
const client = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Authorization': `Token ${localStorage.getItem('authToken')}`,
  },
});
```

### Error 7: 502 Bad Gateway

**Cause**: Backend service crashed or not responding
- Check Render logs
- Verify all environment variables are set
- Check if migrations ran successfully
- Ensure database is accessible

```bash
# View logs in Render dashboard or via CLI:
# Check recent deployments for crash logs
```

### Error 8: "Secret key not set" or "secret key too short"

**Generate secure key**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output to Render environment variable `SECRET_KEY`

---

## Part 9: Step-by-Step Deployment Plan

### Phase 1: Pre-Deployment (Local)

1. **Verify production build**:
   ```bash
   cd frontend && npm run build && cd ..
   python manage.py test  # Run tests
   python manage.py check --deploy  # Django deployment checks
   ```

2. **Update requirements.txt** with all dependencies:
   ```bash
   pip freeze > requirements.txt
   ```

3. **Test migrations**:
   ```bash
   python manage.py migrate --plan
   python manage.py migrate
   ```

### Phase 2: Prepare Render Resources

1. **Create GitHub repo** and push code
2. **Generate SECRET_KEY** for production:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
3. **Create Render account** (render.com)
4. **Connect GitHub** to Render

### Phase 3: Deploy Backend

1. **Create Web Service** in Render:
   - Branch: `main`
   - Build: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start: `gunicorn config.wsgi -w 4 -b 0.0.0.0:10000`

2. **Create PostgreSQL** database in Render

3. **Set environment variables**:
   ```
   DEBUG=False
   SECRET_KEY=[your generated key]
   ALLOWED_HOSTS=your-backend.onrender.com
   DB_NAME=esg_db
   DB_USER=postgres
   DB_PASSWORD=[strong password]
   DB_HOST=[render postgres host]
   DB_PORT=5432
   CORS_ALLOWED_ORIGINS=https://your-frontend.onrender.com
   CSRF_TRUSTED_ORIGINS=https://your-frontend.onrender.com
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

4. **Deploy and test**:
   ```bash
   curl -I https://your-backend.onrender.com/api/
   # Should return 403 Forbidden (requires auth), not 500 error
   ```

### Phase 4: Deploy Frontend

1. **Create Static Site** in Render:
   - Build: `cd frontend && npm install && npm run build`
   - Publish: `frontend/build`

2. **Set environment variables**:
   ```
   REACT_APP_API_URL=https://your-backend.onrender.com/api
   ```

3. **Deploy and test**:
   - Visit frontend domain
   - Try logging in
   - Verify API calls work

### Phase 5: Post-Deployment

1. **Monitor**:
   - Check Render logs daily for errors
   - Set up error tracking (Sentry, etc.)

2. **Backup**:
   - Enable automatic PostgreSQL backups
   - Test restore process monthly

3. **Scaling**:
   - Monitor resource usage
   - Scale up if needed

4. **Updates**:
   - Keep dependencies updated
   - Re-test locally before deployment

---

## Part 10: Additional Recommendations

### Monitoring & Logging

```bash
# Install Sentry for error tracking
pip install sentry-sdk

# In settings.py:
import sentry_sdk
sentry_sdk.init(
    dsn=config('SENTRY_DSN', default=''),
    traces_sample_rate=0.1,
    environment=config('ENVIRONMENT', default='production'),
)
```

### Rate Limiting (Optional but Recommended)

```bash
pip install djangorestframework-ratelimit
```

### Automated Backups

- Render PostgreSQL → enable automated backups
- Set retention to 30+ days
- Test restore monthly

### Custom Domain Setup

1. Buy domain (Namecheap, Google Domains, etc.)
2. Add custom domain in Render (for backend and frontend)
3. Update ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS
4. Redeploy

---

## Quick Reference: Key Files to Update

1. **`backend/config/settings.py`** - Security, CORS, static files
2. **`backend/requirements.txt`** - Dependencies (including whitenoise, gunicorn)
3. **`frontend/package.json`** - Build scripts (already correct)
4. **`.env.example`** - Document all required variables
5. **`Procfile`** (if needed) - For Render build/start commands

---

## Testing Checklist Before Going Live

```bash
# 1. Run security checks
python manage.py check --deploy

# 2. Test with DEBUG=False locally
DEBUG=False python manage.py runserver

# 3. Build frontend
npm run build

# 4. Test static files
python manage.py collectstatic --noinput

# 5. Run migrations
python manage.py migrate

# 6. Create test admin user
python manage.py createsuperuser

# 7. Test API endpoints with auth
curl -H "Authorization: Token YOUR_TOKEN" \
     https://localhost:8000/api/ingestion/batches/
```

---

**You're ready to deploy!** Follow the step-by-step plan in Part 9 and reference the 
error solutions in Part 8 if you encounter any issues.
