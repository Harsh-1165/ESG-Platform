# ESG Data Ingestion Platform - 4-Day MVP Prototype

Complete Django + React prototype for ESG data ingestion, normalization, and approval workflow.

## What's Included

### Backend (Django)
- ✅ Multi-tenant Organization model
- ✅ CSV upload & parsing (SAP Fuel only for MVP)
- ✅ Normalization pipeline (3 source types prepared)
- ✅ Unit conversion (diesel liters → kg CO2e)
- ✅ Approval workflow (pending → approved/rejected/locked)
- ✅ Audit trail (complete change tracking)
- ✅ PostgreSQL ORM with migrations
- ✅ REST API with DRF ViewSets

### Frontend (React)
- ✅ 5-page SPA (Dashboard, Upload, Normalized Data, Approvals, Audit)
- ✅ Multi-file table views with pagination
- ✅ File upload with feedback
- ✅ Approval modal workflow
- ✅ API client with organization headers
- ✅ Responsive layout with sidebar navigation

### Quick Start

#### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with PostgreSQL credentials
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Seeded credentials: admin / admin123

#### Frontend
```bash
cd frontend
npm install
npm start
```

Sets up to `http://localhost:3000`

### Demo Flow

1. **Login**: Use seeded admin account (hardcoded for MVP)
2. **Upload**: Go to "Upload Data" → select SAP_FUEL → upload CSV
3. **Normalize**: System auto-normalizes uploaded rows to kg CO2e
4. **Approve**: Go to "Approvals" → review records → approve/reject
5. **Audit**: View "Audit Log" for all changes

### Sample CSV Format (SAP_FUEL)

```
Date,Quantity,Unit,Facility
2026-01-15,100,liters_diesel,Building A
2026-01-16,150,liters_diesel,Building B
2026-01-17,200,liters_gasoline,Fleet
```

Fields auto-convert to kg CO2e using factors:
- liters_diesel → 2.64 kg CO2e/liter
- liters_gasoline → 2.31 kg CO2e/liter

### MVP Scope

**What Works:**
- Single input source (SAP_FUEL) fully tested
- Basic CSV parsing with validation
- Unit normalization with hardcoded factors
- Approval state machine (pending → approved/rejected/locked)
- Complete audit trail
- Multi-tenant isolation via header
- Dashboard with stats
- All CRUD operations

**What's Out of Scope (Phase 2):**
- User authentication (JWT/OAuth - hardcoded admin only)
- Multi-source full support (framework exists, not tested)
- Advanced anomaly detection (placeholder confidence_score)
- Flagged row review UI
- Edit history with reverts
- Real-time updates
- Advanced reporting
- Mobile optimization
- Production-grade error handling

### Architecture Decisions

1. **CSV → JSON Storage**: Easy MVP, migrate to S3 later
2. **Fixed Emission Factors**: Hardcoded, org-customization in phase 2
3. **No Task Queue**: Simple sync normalization, add Celery when >1K records
4. **Column-based Scope**: Auto-mapped (Fuel=Scope1, Electricity=Scope2, Travel=Scope3)
5. **Confidence Score MVP**: Always 100, add ML detection in phase 2

### File Structure

```
d:\Breathe ESG\
├── backend/
│   ├── config/           # Django settings
│   ├── apps/
│   │   ├── core/         # Organization, User
│   │   ├── ingestion/    # Upload, parsing
│   │   ├── normalization/  # Pipeline, units
│   │   ├── approval/     # Workflow, audit
│   │   └── api/          # REST routes
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── api/          # Axios client
│   │   ├── pages/        # 5 main pages
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   ├── README.md
│   └── .env.example
└── README.md (this file)
```

### Key Models

**Organization**
- Multi-tenant boundary
- Settings (emission factors, defaults)

**RawData + RawDataRow**
- Batch metadata + individual records
- Validation errors, flagging

**NormalizedRecord**
- Final emission quantity + unit
- Confidence score, conversion metadata

**ApprovalRecord**
- Status (pending/approved/rejected/locked)
- Reviewer + timestamp

**AuditLog**
- Complete change history
- Old/new values for every action

### API Example

Upload file as admin:

```bash
curl -X POST http://localhost:8000/api/ingestion/batches/upload/ \
  -H "X-Organization-ID: {org-id}" \
  -H "Authorization: Token {admin-token}" \
  -F "file=@data.csv" \
  -F "source_type=SAP_FUEL"
```

Get pending approvals:

```bash
curl http://localhost:8000/api/approval/records/pending/ \
  -H "X-Organization-ID: {org-id}" \
  -H "Authorization: Token {token}"
```

Approve a record:

```bash
curl -X POST http://localhost:8000/api/approval/records/{record-id}/approve/ \
  -H "X-Organization-ID: {org-id}" \
  -H "Authorization: Token {token}" \
  -H "Content-Type: application/json" \
  -d '{"comment": "Looks good"}'
```

### Testing the Prototype

**Full workflow (10 min):**

1. Backend: Start server, load seed data
2. Frontend: Visit dashboard (see 3 demo records pending)
3. Upload: Mock new CSV (system creates batch + rows)
4. Normalize: Click batch → auto-normalizes to CO2e
5. Approve: Go to approvals, review records
6. Audit: See all changes in audit log

**Manual CSV test:**

Create `test_fuel.csv`:
```
Date,Quantity,Unit,Facility
2026-02-01,50,liters_diesel,HQ
2026-02-02,75,liters_gasoline,Remote
```

Upload via UI → System creates 2 NormalizedRecords

### Deployment

**Development:**
- Both services run locally
- SQLite or local PostgreSQL
- No Docker needed

**Production (phase 2):**
- Backend: Heroku/Railway/AWS
- Frontend: Vercel/Netlify
- Database: Managed PostgreSQL
- Storage: S3/GCS for CSV files
- Auth: Auth0 or Firebase

### Performance Notes

MVP designed for <100 records. To scale beyond:
- Add indices on `(organization_id, created_at)`
- Implement pagination (done in API)
- Add task queue for normalization (Celery)
- Migrate to async handlers (Django async views)
- Add caching (Redis)

### Support & Troubleshooting

**Backend won't start?**
- Check PostgreSQL is running
- Verify `.env` has correct credentials
- Run `python manage.py migrate`

**Frontend API calls fail?**
- Verify backend is at `http://localhost:8000`
- Check `X-Organization-ID` header is set
- Clear browser localStorage

**Database errors?**
- Delete migrations, run `makemigrations + migrate` again
- Check `apps.py` files have correct labels

### Next Steps After MVP

1. **Authentication** (Day 5)
   - Add login form
   - JWT token generation
   - User session management

2. **Multi-Source Support** (Week 2)
   - Enable UTILITY_ELECTRICITY parser
   - Enable TRAVEL parser
   - Add source-specific validation

3. **Anomaly Detection** (Week 3)
   - Historical variance scoring
   - Outlier detection algorithms
   - Confidence thresholds

4. **Advanced Features** (Week 4)
   - Export to Excel/PDF
   - Bulk approval
   - Custom emission factors per org
   - Real-time notifications
   - Mobile app

### Contact & Questions

See backend/README.md and frontend/README.md for detailed docs.

---

**Built for demonstration purposes.** Ready for 4-day prototype evaluation.
