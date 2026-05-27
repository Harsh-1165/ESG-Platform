# ESG Data Ingestion Platform - Backend

Django REST Framework API for ESG data ingestion, normalization, and approval workflow.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update PostgreSQL credentials:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials.

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data  # Load demo data
python manage.py createsuperuser  # Create admin user (or use seeded admin/admin123)
```

### 4. Run Development Server

```bash
python manage.py runserver
```

API available at `http://localhost:8000/api/`

## API Endpoints

### Ingestion
- `POST /api/ingestion/batches/upload/` - Upload CSV file
- `GET /api/ingestion/batches/` - List upload batches
- `GET /api/ingestion/batches/{id}/rows/` - Get rows in batch
- `PATCH /api/ingestion/batches/{id}/flag_row/` - Flag suspicious row

### Normalization
- `GET /api/normalization/records/` - List normalized records
- `GET /api/normalization/records/{id}/` - Get record detail
- `POST /api/normalization/records/normalize_batch/` - Normalize a batch
- `PATCH /api/normalization/records/{id}/update_record/` - Update record values
- `GET /api/normalization/records/{id}/history/` - Get change history

### Approval
- `GET /api/approval/records/pending/` - Get pending approvals
- `POST /api/approval/records/{id}/approve/` - Approve record
- `POST /api/approval/records/{id}/reject/` - Reject record
- `POST /api/approval/records/{id}/lock/` - Lock record (immutable)

### Audit
- `GET /api/audit/logs/` - View audit trail

## Multi-Tenancy

All requests require the `X-Organization-ID` header:

```bash
curl -H "X-Organization-ID: {org-uuid}" http://localhost:8000/api/...
```

## Authentication

Use token auth:

```bash
curl -H "Authorization: Token {token}" http://localhost:8000/api/...
```

## Key Features

✅ Multi-tenant isolation  
✅ CSV upload + parsing (SAP, Utility, Travel)  
✅ Unit normalization (liters → kg CO2e)  
✅ Approval workflow (pending → approved/rejected/locked)  
✅ Complete audit trail  
✅ Django admin for management  

## Project Structure

```
backend/
├── config/          # Django settings + middleware
├── apps/
│   ├── core/        # Organization + User models
│   ├── ingestion/   # CSV upload + parsing
│   ├── normalization/  # Emission calculation + pipeline
│   ├── approval/    # Workflow + audit logs
│   └── api/         # REST routes
└── manage.py
```

## Development Notes

- **Emissions**: Values stored as Decimal for precision
- **Units**: Auto-converts to metric tons if >1000 kg
- **Confidence**: Fixed at 100 for MVP (add anomaly detection in phase 2)
- **Storage**: Raw CSV stored as JSON in DB (add S3 in phase 2)

## Troubleshooting

**Import errors?** Ensure all apps are registered in `settings.py` INSTALLED_APPS

**Migrations fail?** Delete `db.sqlite3` and run migrations again

**Permission denied?** Check user is member of organization via OrganizationUser

## Next Steps

1. Implement real anomaly detection
2. Add multi-source CSV parsing
3. Deploy to cloud (Heroku/Railway/AWS)
4. Add email notifications
5. Implement background job queue (Celery)
