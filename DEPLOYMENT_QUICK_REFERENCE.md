# Deployment Quick Reference

Essential commands and configurations at a glance.

---

## Local Pre-Deployment Commands

```bash
# 1. Update requirements
pip freeze > requirements.txt

# 2. Test with production settings
DEBUG=False python manage.py runserver

# 3. Check deployment readiness
python manage.py check --deploy

# 4. Create migrations
python manage.py makemigrations

# 5. Preview migrations
python manage.py migrate --plan

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Build frontend
cd frontend
npm run build
cd ..

# 8. Run tests
pytest
npm test

# 9. Generate SECRET_KEY for production
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Essential Environment Variables

### Production Backend

```
DEBUG=False
SECRET_KEY=[NEW_KEY_GENERATED_ABOVE]
ENVIRONMENT=production
ALLOWED_HOSTS=your-domain.com,your-domain.onrender.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=esg_db
DB_USER=postgres
DB_PASSWORD=[STRONG_PASSWORD]
DB_HOST=[RENDER_HOST]
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
```

### Production Frontend

```
REACT_APP_API_URL=https://your-backend-domain.com/api
```

---

## Render.com Deployment Summary

### Backend Web Service

| Setting | Value |
|---------|-------|
| Environment | Python 3 |
| Build Cmd | `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput` |
| Start Cmd | `gunicorn config.wsgi -w 4 -b 0.0.0.0:10000` |

### Frontend Static Site

| Setting | Value |
|---------|-------|
| Build Cmd | `cd frontend && npm install && npm run build` |
| Publish Dir | `frontend/build` |

### PostgreSQL Database

- Create in Render
- Copy connection string to env variables
- Enable automatic backups

---

## Common Issues & Quick Fixes

| Issue | Fix |
|-------|-----|
| 502 Bad Gateway | Check logs: `render logs [service-id]` |
| CORS error | Update `CORS_ALLOWED_ORIGINS` and redeploy |
| Database 500 error | Check `DB_HOST`, `DB_PASSWORD` in env vars |
| Static files 404 | Ensure `collectstatic` runs in build command |
| ModuleNotFoundError | Add package to `requirements.txt` and redeploy |
| `ALLOWED_HOSTS` validation | Update `ALLOWED_HOSTS` in env vars |
| Frontend shows "Cannot GET" | Check `REACT_APP_API_URL` is set |

---

## Testing the Deployment

```bash
# 1. Test backend health
curl -I https://your-backend.onrender.com/api/

# 2. Expected response
# HTTP/2 403 Forbidden (requires auth, which is fine)
# NOT 500 Internal Server Error

# 3. Test frontend loads
# Visit https://esg-frontend-prod.onrender.com
# Check browser console (F12) for errors

# 4. Test API call
# In browser console (with token):
# fetch('https://your-backend.com/api/ingestion/batches/', {
#   headers: {
#     'Authorization': 'Token YOUR_TOKEN'
#   }
# }).then(r => r.json()).then(console.log)
```

---

## Database Operations

```bash
# Create backup
pg_dump -U postgres -h $DB_HOST -d $DB_NAME > backup.sql

# Restore backup
psql -U postgres -h $DB_HOST -d $DB_NAME < backup.sql

# Run migrations
python manage.py migrate

# Rollback migrations
python manage.py migrate [app_name] [migration_number]

# Check migration status
python manage.py showmigrations
```

---

## File Locations

```
d:\Breathe ESG\
├── DEPLOYMENT.md              ← Full deployment guide
├── RENDER_DEPLOYMENT.md       ← Render.com specific
├── DEPLOYMENT_CHECKLIST.md    ← Pre-deployment checklist
├── backend\
│   ├── config\
│   │   ├── settings.py        ← Update for production
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── requirements.txt        ← Add whitenoise, gunicorn
│   └── .env.example           ← Document all vars
└── frontend\
    ├── package.json
    ├── .env.example
    └── src\
        └── api\
            └── client.js      ← Check REACT_APP_API_URL
```

---

## Security Checklist (Minimal)

- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is unique and random
- [ ] `ALLOWED_HOSTS` is correct
- [ ] `CORS_ALLOWED_ORIGINS` is restrictive
- [ ] HTTPS enabled (automatic on Render)
- [ ] Database password is strong
- [ ] No credentials in code
- [ ] Backups enabled

---

## Monitoring After Deploy

### First Hour
- Monitor error logs
- Test all main features
- Check API response times

### First Day
- Continue monitoring
- Check database size
- Verify backups ran

### Ongoing
- Review logs daily
- Monitor performance weekly
- Test backups monthly

---

## Render Dashboard Navigation

1. **Services** → View all deployments
2. **Logs** → Real-time service logs
3. **Metrics** → CPU, memory, requests
4. **Settings** → Environment variables, restart
5. **Events** → Deployment history
6. **Alert** → Email notifications

---

## Rollback (Emergency)

```bash
# Quick rollback without redeploy
git revert [bad-commit]
git push origin main
# Automatic redeploy triggered

# Or manually trigger from Render dashboard
# Service → Latest Deploy → Redeploy
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| API response time | < 200ms |
| Frontend load time | < 3 seconds |
| Auth token refresh | < 500ms |
| Database query | < 100ms |
| Static file size | < 100KB (gzipped) |

---

## Support Resources

- **Django Docs**: https://docs.djangoproject.com
- **DRF Docs**: https://www.django-rest-framework.org
- **Render Docs**: https://render.com/docs
- **React Docs**: https://react.dev
- **Security**: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist

---

## Key Contacts (Optional)

| Role | Contact |
|------|---------|
| DevOps Lead | [Your name] |
| Backend Owner | [Your name] |
| Frontend Owner | [Your name] |
| On-Call | [Phone/Email] |

---

## Deployment Timeline

| Time | Task |
|------|------|
| T-05min | Final backup of production |
| T-00min | Deploy backend |
| T+02min | Verify backend health |
| T+03min | Deploy frontend |
| T+05min | Verify frontend loads |
| T+10min | Run smoke tests |
| T+15min | Monitor logs |
| T+30min | Status check |
| T+1hr | Full verification |

---

## Emergency Contacts

🚨 If things go wrong:

1. **Check logs** first (99% of issues visible in logs)
2. **Rollback** if needed (revert last commit)
3. **Restore database** if corrupted (from backup)
4. **Contact platform support** if infrastructure issue

---

**Keep this page bookmarked for easy reference during deployment!**

Generated: 2026-05-27
Last Updated: [Update this when you change deployment process]
