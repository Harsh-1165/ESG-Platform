# Pre-Deployment Checklist

Use this checklist to verify your application is ready for production deployment.

---

## Code Quality

- [ ] No `print()` statements left in code
- [ ] No commented-out code blocks
- [ ] All TODOs and FIXMEs resolved or documented
- [ ] No hardcoded credentials or secrets in code
- [ ] All imports are used (no unused imports)
- [ ] Code follows PEP 8 style guide
- [ ] No `console.log()` statements in production frontend code

```bash
# Run linter
flake8 backend/
pylint backend/
```

---

## Environment & Configuration

### Backend

- [ ] `.env` file NOT in version control (check `.gitignore`)
- [ ] `.env.example` contains all required variables
- [ ] `DEBUG=False` in production environment
- [ ] `SECRET_KEY` is a valid long random string (not the default)
- [ ] `ALLOWED_HOSTS` correctly configured for your domain
- [ ] `CORS_ALLOWED_ORIGINS` points to frontend domain
- [ ] `CSRF_TRUSTED_ORIGINS` configured for security
- [ ] Database credentials different from development
- [ ] Email backend configured (if needed)

### Frontend

- [ ] `.env` file NOT in version control
- [ ] `REACT_APP_API_URL` points to production backend
- [ ] No demo auth tokens in environment variables
- [ ] Build completes without warnings: `npm run build`
- [ ] No `localhost` or `127.0.0.1` references

---

## Security

- [ ] HTTPS enabled (automatically on most platforms)
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_HSTS_SECONDS` set to 31536000
- [ ] CORS headers properly configured
- [ ] SQLi protection enabled (Django ORM does this by default)
- [ ] XSS protection headers set
- [ ] Rate limiting considered (optional but recommended)

```python
# Check Django security checklist
python manage.py check --deploy
```

---

## Database

- [ ] PostgreSQL running (not SQLite)
- [ ] Database user has limited permissions
- [ ] Database password is strong
- [ ] All migrations created: `python manage.py makemigrations`
- [ ] All migrations reversible and tested
- [ ] Migration plan reviewed: `python manage.py migrate --plan`
- [ ] Database backup strategy in place
- [ ] Connection pooling configured (CONN_MAX_AGE)

```bash
# Test migrations
python manage.py migrate --plan
python manage.py migrate
```

---

## Static Files & Assets

- [ ] WhiteNoise installed: `pip list | grep -i whitenoise`
- [ ] `STATIC_ROOT` configured correctly
- [ ] `STATICFILES_STORAGE` set to CompressedManifestStaticFilesStorage
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Admin CSS/JS loads correctly
- [ ] React build optimized

```bash
# Collect static files
python manage.py collectstatic --noinput

# Check file sizes
ls -lh staticfiles/
```

---

## Dependencies

- [ ] `requirements.txt` updated: `pip freeze > requirements.txt`
- [ ] Includes `gunicorn` for production server
- [ ] Includes `whitenoise` for static files
- [ ] No development-only packages in production (pytest, etc. marked dev)
- [ ] All packages pinned to specific versions
- [ ] `package.json` has all required dependencies

```bash
# Update requirements
pip freeze > requirements.txt

# Check for outdated packages
pip list --outdated
```

---

## Testing

- [ ] Unit tests pass: `pytest`
- [ ] All API endpoints tested
- [ ] Login flow tested
- [ ] File upload tested
- [ ] Frontend builds successfully: `npm run build`
- [ ] Frontend components render without errors
- [ ] Built bundle size reasonable (< 100KB gzipped)
- [ ] Database queries optimized (no N+1 queries)

```bash
# Run tests
pytest
npm test

# Build frontend
npm run build

# Check bundle size
npm run build
ls -lh build/static/js/
```

---

## Production Build Testing

- [ ] Test with `DEBUG=False` locally:

```bash
DEBUG=False python manage.py runserver
```

- [ ] Frontend loads correctly
- [ ] Static files load (CSS, images)
- [ ] API calls work
- [ ] Error pages display correctly (not debug pages)

---

## Monitoring & Logging

- [ ] Logging configured (DEBUG level for prod)
- [ ] Error tracking considered (Sentry, etc.)
- [ ] Email notifications configured
- [ ] Backup strategy in place
- [ ] Monitoring dashboard set up

---

## Documentation

- [ ] `README.md` updated with setup instructions
- [ ] `DEPLOYMENT.md` complete and accurate
- [ ] Environment variables documented (in `.env.example`)
- [ ] API endpoints documented (if applicable)
- [ ] Known issues documented
- [ ] Rollback procedure documented

---

## DNS & Domain (if applicable)

- [ ] Domain is registered
- [ ] DNS configured to point to deployment platform
- [ ] SSL certificate auto-renewed
- [ ] Both www and non-www domains work
- [ ] Redirects configured correctly

---

## Pre-Launch (48 Hours Before)

- [ ] Final code review completed
- [ ] All tests passing
- [ ] Performance testing done (target: < 2 second response time)
- [ ] Backup taken of production database
- [ ] Rollback plan documented
- [ ] On-call support identified
- [ ] Runbook created for common issues

---

## Launch Day

### Before Going Live

- [ ] All team members notified
- [ ] Maintenance window (if needed) scheduled
- [ ] Database backed up
- [ ] Environment variables double-checked
- [ ] Monitoring active
- [ ] Error tracking active
- [ ] Support team on standby

### Deployment

1. [ ] Deploy backend
   ```bash
   # On platform (Render, Heroku, etc.)
   # Should automatically:
   # - pip install -r requirements.txt
   # - python manage.py migrate
   # - python manage.py collectstatic --noinput
   ```

2. [ ] Verify backend:
   ```bash
   curl -I https://your-backend-domain.com/api/
   # Should return 403 or 400, NOT 500
   ```

3. [ ] Deploy frontend
   ```bash
   # Platform builds and deploys
   ```

4. [ ] Verify frontend:
   - Load frontend URL in browser
   - Check browser console for errors
   - Try an API call
   - Check Network tab for correct backend URL

5. [ ] Smoke tests:
   - [ ] Login works
   - [ ] Main page loads
   - [ ] API endpoints respond
   - [ ] Database queries succeed
   - [ ] Static files load
   - [ ] HTTPS works (no mixed content)

### Post-Launch (First 24 Hours)

- [ ] Monitor error logs
- [ ] Monitor performance metrics
- [ ] Test all major features
- [ ] Verify database backups work
- [ ] Check email notifications (if applicable)
- [ ] Review user feedback

---

## Common Pre-Launch Issues to Avoid

| Issue | Solution |
|-------|----------|
| Static files 404 | Run `collectstatic` before deployment |
| CORS errors | Update `CORS_ALLOWED_ORIGINS` |
| Database connection failed | Check credentials and network |
| Secret key error | Generate new key, don't reuse dev key |
| Import errors | Ensure all dependencies in `requirements.txt` |
| Missing migrations | Run `migrate` in build command |
| API returns 500 | Check logs, verify environment variables |
| Frontend shows wrong API URL | Check `REACT_APP_API_URL` |

---

## Post-Launch Monitoring

### Daily

- [ ] Check error logs
- [ ] Verify backups ran
- [ ] Monitor database size

### Weekly

- [ ] Review performance metrics
- [ ] Check for abandoned connections
- [ ] Update security patches

### Monthly

- [ ] Review failed requests
- [ ] Optimize slow queries
- [ ] Test database restore procedure
- [ ] Review logs for patterns

---

## Rollback Plan

If something goes wrong, you should be able to rollback quickly:

### Option 1: Redeploy Previous Version

```bash
git revert [commit-hash]
git push
# Automatic redeploy triggered
```

### Option 2: Database Rollback

```bash
# Restore from latest backup
python manage.py migrate [previous-migration]
```

### Option 3: Frontend Rollback

```bash
git checkout [previous-tag]
git push
# Static site auto-redeploys
```

### Option 4: Feature Flag

Use feature flags to disable problematic features without redeploying:

```python
# In settings.py
FEATURE_NEW_UPLOAD = config('FEATURE_NEW_UPLOAD', default=False, cast=bool)

# In views.py
if settings.FEATURE_NEW_UPLOAD:
    # Use new code
else:
    # Use old code
```

---

## Final Verification

Before clicking "deploy" the final time:

```bash
# Run Django checks
python manage.py check --deploy

# Test database migration
python manage.py migrate --plan

# Test static files
python manage.py collectstatic --noinput --dry-run

# Test frontend build
npm run build

# Verify no secrets in code
git log --patch -- | grep -i "password\|secret\|key" || echo "No secrets found"
```

---

## Success Criteria

Your deployment is successful when:

- ✅ Frontend loads without errors
- ✅ API calls return expected responses
- ✅ Login/authentication works
- ✅ Database reads and writes work
- ✅ Static files load (CSS, images)
- ✅ No console errors
- ✅ Response times < 2 seconds
- ✅ Error logs are clean (no critical warnings)
- ✅ Backups are running
- ✅ Monitoring is active

---

**Good luck with your deployment! 🚀**

Remember: **It's better to deploy slowly and carefully than quickly and regret it.**
