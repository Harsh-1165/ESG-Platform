# Deployment Documentation Overview

This folder contains comprehensive deployment guides for the ESG Platform. Here's what you have:

---

## 📋 Documentation Files

### 1. **DEPLOYMENT.md** (Main Guide - START HERE)
The most comprehensive guide covering:
- ✅ Production readiness checklist (all components)
- ✅ Environment variables (with examples)
- ✅ CORS configuration
- ✅ Static files setup
- ✅ Database configuration & migration strategy
- ✅ Frontend build commands
- ✅ Common deployment errors & solutions (8 specific issues)
- ✅ Step-by-step deployment plan (5 phases)

**When to read**: Before you start any deployment work

---

### 2. **RENDER_DEPLOYMENT.md** (Platform-Specific)
Step-by-step instructions for Render.com specifically:
- ✅ Prerequisites (GitHub account, Render account)
- ✅ Connecting GitHub to Render
- ✅ Configuring backend service
- ✅ Creating PostgreSQL database
- ✅ Setting all environment variables
- ✅ Deploying frontend as Static Site
- ✅ Testing the full application
- ✅ Custom domain setup
- ✅ Database backups
- ✅ Monitoring & alerts
- ✅ Troubleshooting guide

**When to read**: When deploying to Render.com

---

### 3. **DEPLOYMENT_CHECKLIST.md** (Pre-Launch Verification)
Interactive checklist covering:
- ✅ Code quality checks
- ✅ Environment & configuration
- ✅ Security verification
- ✅ Database readiness
- ✅ Static files & assets
- ✅ Dependencies
- ✅ Testing requirements
- ✅ Production build testing
- ✅ Monitoring setup
- ✅ Documentation
- ✅ DNS & domain
- ✅ Pre-launch (48 hours before)
- ✅ Launch day procedures
- ✅ Post-launch monitoring
- ✅ Rollback procedures

**When to read**: The day before deployment (print it out!)

---

### 4. **DEPLOYMENT_QUICK_REFERENCE.md** (Bookmark This)
One-page quick reference with:
- ✅ Essential commands (copy-paste ready)
- ✅ Required environment variables
- ✅ Render deployment summary table
- ✅ Common issues & quick fixes
- ✅ Database operations
- ✅ File locations
- ✅ Security checklist
- ✅ Performance targets
- ✅ Emergency procedures

**When to read**: During deployment (keep a browser tab open)

---

## 🚀 Quick Start: Deployment Path

### Path A: First Time Deploying?

1. **Read**: [DEPLOYMENT.md](./DEPLOYMENT.md) - Parts 1-3 (30 min)
2. **Prepare**: Follow Part 9 Phase 1 (Local prep) - 1 hour
3. **Read**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Get familiar - 15 min
4. **Read**: [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) - Steps 1-5 - 20 min
5. **Deploy**: Follow [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) - Steps 6-12 - 30 min
6. **Verify**: Use [DEPLOYMENT_QUICK_REFERENCE.md](./DEPLOYMENT_QUICK_REFERENCE.md) - Testing section - 10 min

**Total time**: ~2.5 hours

### Path B: Re-deploying After Code Changes?

1. **Update code** in `backend/` or `frontend/`
2. **Check**: [DEPLOYMENT_QUICK_REFERENCE.md](./DEPLOYMENT_QUICK_REFERENCE.md) - Local Pre-Deployment Commands
3. **Push**: `git push origin main`
4. **Auto-deploy**: Render automatically deploys (5-10 min)
5. **Verify**: Test frontend and API

**Total time**: ~15 minutes

### Path C: Something Broke in Production?

1. **Check logs**: [DEPLOYMENT_QUICK_REFERENCE.md](./DEPLOYMENT_QUICK_REFERENCE.md) - Monitoring section
2. **Find issue**: [DEPLOYMENT.md](./DEPLOYMENT.md) - Part 8 (Common Errors)
3. **Fix**: Rollback or apply fix
4. **Verify**: Test again

**Total time**: Depends on issue (typically 15-45 min)

---

## 📁 Key Files Modified for Deployment

### Backend
- **`backend/config/settings.py`** ✅ Updated
  - Added WhiteNoise middleware
  - Added production security settings
  - Production-ready CORS & CSRF configuration
  - Database connection pooling ready

- **`backend/requirements.txt`** ✅ Updated
  - Added `whitenoise==6.6.0` (static file serving)
  - Added `gunicorn==21.2.0` (production server)

- **`backend/.env.example`** ✅ Updated
  - Documented all environment variables
  - Added development and production sections
  - Includes example values and explanations

### Frontend
- No code changes needed - all configuration via environment variables

---

## 🔑 Critical Environment Variables

### Must Haves (Production)

```
DEBUG=False                                    # CRITICAL: Must be False!
SECRET_KEY=[new random key]                   # CRITICAL: Generate new!
ALLOWED_HOSTS=your-domain.onrender.com        # Your actual domain
DB_NAME=esg_db                                # Database name
DB_USER=postgres                              # Database user
DB_PASSWORD=[strong password]                 # Use Render-provided password
DB_HOST=[render postgres host]                # From Render dashboard
CORS_ALLOWED_ORIGINS=https://your-frontend   # Your frontend domain
REACT_APP_API_URL=https://your-backend/api   # API endpoint URL
```

### Optional but Recommended

```
ENVIRONMENT=production
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## ✅ Before Clicking "Deploy"

- [ ] Read at least Parts 1-3 of DEPLOYMENT.md
- [ ] Complete the DEPLOYMENT_CHECKLIST.md
- [ ] Backend: `python manage.py check --deploy` passes
- [ ] Frontend: `npm run build` completes without errors
- [ ] SECRET_KEY is NEW (not reused from development)
- [ ] All environment variables are documented
- [ ] Database backups are enabled
- [ ] Error monitoring is ready (optional but advised)

---

## 🆘 Common Questions

### "What if the deployment fails?"
→ Check logs in Render dashboard, reference [DEPLOYMENT.md Part 8](./DEPLOYMENT.md#part-8-common-deployment-errors--solutions)

### "How do I rollback?"
→ See [DEPLOYMENT_CHECKLIST.md Rollback Plan](./DEPLOYMENT_CHECKLIST.md#rollback-plan)

### "What if I forgot to set an environment variable?"
→ Update in Render dashboard → Click service → Settings → Environment → Update variable → Auto-redeploy

### "Can I test the build locally before deploying?"
→ Yes! [DEPLOYMENT.md Part 9 Phase 1](./DEPLOYMENT.md#phase-1-pre-deployment-local) shows how

### "How do I generate a SECRET_KEY?"
→ [DEPLOYMENT_QUICK_REFERENCE.md](./DEPLOYMENT_QUICK_REFERENCE.md) has the command

### "Is my password secure enough?"
→ Render generates strong ones. If you create your own, use 20+ characters, mix uppercase/lowercase/numbers/symbols

### "How long does deployment take?"
→ 5-10 minutes typically. Backend build is longer due to Python packages.

---

## 📊 Deployment Checklist Status

| Item | Status | Location |
|------|--------|----------|
| Production settings | ✅ Ready | `backend/config/settings.py` |
| Environment variables | ✅ Template created | `backend/.env.example` |
| CORS configured | ✅ Ready | `backend/config/settings.py` |
| Static files setup | ✅ WhiteNoise added | `backend/config/settings.py` |
| Database config | ✅ Ready | Part of settings.py |
| Frontend build | ✅ Tested locally | `npm run build` |
| Deployment docs | ✅ Complete | 4 markdown files |
| Error solutions | ✅ Documented | `DEPLOYMENT.md` Part 8 |
| Deployment plan | ✅ Detailed | `DEPLOYMENT.md` Part 9 |

---

## 🎯 Success Criteria

Your deployment is successful when:

✅ Frontend loads in browser (no errors in console)
✅ Can log in to the application
✅ API calls return data (not 500 errors)
✅ Static files load (CSS, images visible)
✅ Database queries work
✅ Error logs are clean

---

## 📞 Support Resources

- **Django Security Checklist**: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist
- **Render Docs**: https://render.com/docs
- **Django REST Framework**: https://www.django-rest-framework.org
- **React Production Build**: https://create-react-app.dev/docs/production-build

---

## 📌 Pro Tips

1. **Deploy at low-traffic times** (not during business hours initially)
2. **Monitor logs for 30 minutes** after deployment
3. **Have a rollback plan ready** (tested before going live)
4. **Backup database before each deployment** (Render does this auto)
5. **Test locally with `DEBUG=False`** before production deployment
6. **Use meaningful git commit messages** for easy rollback
7. **Document any deployment issues** for future reference

---

## Next Steps

1. ✅ Read [DEPLOYMENT.md](./DEPLOYMENT.md) (Parts 1-3)
2. ✅ Prepare environment variables (from `.env.example`)
3. ✅ Run local pre-deployment checks
4. ✅ Print [DEPLOYMENT_QUICK_REFERENCE.md](./DEPLOYMENT_QUICK_REFERENCE.md)
5. ✅ Follow [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
6. ✅ Test the deployed application thoroughly

---

**You've got this! 🚀**

Generated: May 27, 2026
Keep these docs handy for future deployments!
