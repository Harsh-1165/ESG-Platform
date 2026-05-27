# ESG Data Ingestion Platform

An end-to-end ESG (emissions) ingestion, normalization, analyst approval, and immutable audit-trail platform.

This repo contains:
- `frontend/`: React app for uploading CSVs and reviewing/approving normalized emissions records
- `backend/`: Django REST Framework API providing multi-tenant ingestion, normalization, approval workflow, and audit logs

## How it works (high level)
1. **Ingest raw data**: Upload a CSV to create an ingestion batch and per-row raw records (with basic validation/flagging for missing required fields).
2. **Normalize**: Convert raw rows into **normalized emission records** (calculate CO2e using source-specific emission factors; run validation and set suspicious/confidence).
3. **Approval workflow**: Analysts can **approve / reject / lock** normalized records.
4. **Audit trail**: Key actions are recorded to an immutable audit log and exposed via the API.

## Tech stack
- Frontend: React (react-scripts), Axios
- Backend: Django + Django REST Framework (token auth), Postgres (recommended)
- Multi-tenancy: `X-Organization-ID` request header filters all data-access endpoints

## Prerequisites
- **Python 3.10+**
- **Node.js** (for `frontend/`)
- **PostgreSQL** (recommended)
- Tools:
  - `pip` / `python -m pip`
  - `npm`

## Repo structure
- `frontend/`
  - React pages for dashboard, upload, normalized records, approvals, record detail, and audit log
  - API client wrappers under `frontend/src/api/`
- `backend/`
  - Django REST API with viewsets under `backend/apps/*/`
  - CSV parsing under `backend/apps/ingestion/`
  - Normalization pipeline and validations under `backend/apps/normalization/`
  - Approval workflow under `backend/apps/approval/`
  - Audit log model helpers under `backend/apps/audit/`

## Local development (both frontend + backend)

### 1) Backend setup
From repo root (`D:\Breathe ESG`):

1. Create and activate a virtualenv:
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```powershell
   cp .env.example .env
   ```
   Update at least:
   - `SECRET_KEY`
   - DB settings: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (and `DB_ENGINE` if needed)
   - CORS settings: `CORS_ALLOWED_ORIGINS` (ensure your frontend origin is included, usually `http://localhost:3000`)

   Notes (from backend settings):
   - Requests are authenticated using DRF Token Auth.
   - Data access is multi-tenant using the `X-Organization-ID` header.

4. Create DB schema and seed demo data:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_data
   ```

5. Start the backend:
   ```powershell
   python manage.py runserver
   ```
   API base: `http://localhost:8000/api/`

### 2) Frontend setup
1. Install dependencies:
   ```powershell
   cd frontend
   npm install
   ```

2. Configure environment:
   Copy `.env.example` to `.env` and set `REACT_APP_API_URL`:
   ```powershell
   cp .env.example .env
   ```

   Optional (handy for avoiding manual localStorage setup):
   - `REACT_APP_DEMO_AUTH_TOKEN`
   - `REACT_APP_ORG_ID`

   The frontend uses these values to populate:
   - `localStorage.authToken`
   - `localStorage.orgId`

3. Start the frontend:
   ```powershell
   npm start
   ```
   Frontend: `http://localhost:3000`

## Authentication + organization (multi-tenancy)

### Get a token
The backend exposes DRF token auth at:
- `POST /api/auth/token/`

Seeded demo credentials (from `backend/apps/core/management/commands/seed_data.py`):
- username: `admin`
- password: `admin123`

Example (PowerShell):
```powershell
$body = @{ username = "admin"; password = "admin123" } | ConvertTo-Json
$resp = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/token/" -ContentType "application/json" -Body $body
$token = $resp.token
```

The response includes a token that you must store as:
- `localStorage.authToken`

### Get `orgId` (organization UUID)
All ingestion/normalization/approval/audit endpoints require:
- HTTP header: `X-Organization-ID: <org-uuid>`

How to fetch the seeded organization(s):
1. Call:
   - `GET /api/organizations/`
2. Send:
   - `Authorization: Token <your_token>`

The response includes an `id` (UUID). Put it into:
- `localStorage.orgId`

Alternatively, set `REACT_APP_ORG_ID` in `frontend/.env` so the frontend auto-populates it.

### Where the frontend sends headers
The frontend API client (Axios) sets:
- `X-Organization-ID`: from `localStorage.orgId`
- `Authorization: Token <token>`: from `localStorage.authToken`

## CSV ingestion (supported source types)

Ingestion endpoint:
- `POST /api/ingestion/batches/upload/`

Required multipart fields:
- `file`: the CSV
- `source_type`: one of:
  - `SAP_FUEL`
  - `UTILITY_ELECTRICITY`
  - `TRAVEL`

Optional fields (also accepted by the serializer):
- `data_source_name`
- `data_source_external_id`
- `payload_schema_name`
- `payload_schema_version`

#### `SAP_FUEL` required CSV columns
The SAP fuel parser expects:
- `Date`
- `Quantity`
- `Unit`
- `Facility`

Rows missing any required field are marked with validation errors.

For `UTILITY_ELECTRICITY` and `TRAVEL`, the parsers currently accept rows without strict required-field validation (they still store each row’s raw columns as JSON).

## API endpoints (by feature)

Base URL: `http://localhost:8000/api/`

### Auth
- `POST /api/auth/token/` (Token Auth)

### Organizations (multi-tenant discovery)
- `GET /api/organizations/`

### Ingestion
- `POST /api/ingestion/batches/upload/`
- `GET /api/ingestion/batches/`
- `GET /api/ingestion/batches/{batch_id}/rows/`
- `GET /api/ingestion/batches/{batch_id}/row_detail/?row_id=<row-uuid>`
- `PATCH /api/ingestion/batches/{batch_id}/flag_row/`
  - body: `{ "row_id": "...", "is_flagged": true|false, "flag_reason": "..." }`

### Normalization
- `GET /api/normalization/records/`
- `POST /api/normalization/records/normalize_batch/`
  - body: `{ "batch_id": "<raw-data-batch-uuid>" }`
- `GET /api/normalization/records/{record_id}/`
- `PATCH /api/normalization/records/{record_id}/update_record/`
  - allowed updates (MVP): `emission_quantity`, `emission_unit`, `metric_type`, `facility_id`, `time_period`, `notes`
- `GET /api/normalization/records/{record_id}/history/`

### Approval workflow
- `GET /api/approval/records/pending/`
- `GET /api/approval/records/` (supports `?status=<pending|approved|rejected|locked>` via query params)
- `POST /api/approval/records/{approval_id}/approve/`
  - body: `{ "comment": "..." }`
- `POST /api/approval/records/{approval_id}/reject/`
  - body: `{ "reason": "..." }`
- `POST /api/approval/records/{approval_id}/lock/`
  - body: `{ "reason": "..." }`

### Audit log (immutable trail)
- `GET /api/audit/logs/`
  - supports query params:
    - `action` (e.g., `approved`, `rejected`, `locked`, etc.)
    - `record_type` (e.g., `NormalizedRecord`, `ApprovalRecord`)

## End-to-end workflow (what you can do in the UI)
1. **Dashboard**
   - Shows recent uploads from ingestion batches.
2. **Upload Data**
   - Upload a CSV by source type (creates an ingestion batch).
   - Note: in this MVP, uploading does **not** automatically trigger normalization. You must run normalization separately via:
     - `POST /api/normalization/records/normalize_batch/` (body: `{ "batch_id": "<raw-data-batch-uuid>" }`)
3. **Normalized Data**
   - Browse normalized records and open a record detail view.
4. **Approvals**
   - Review pending records and approve/reject/lock them.
5. **Audit Log**
   - View actions recorded by the backend audit trail.

## Running tests

Backend test runner:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py test
```

There are Django unit/integration tests under `backend/apps/*/tests.py`.

## Troubleshooting

### CORS errors
Ensure `CORS_ALLOWED_ORIGINS` in `backend/.env` includes your frontend origin (typically `http://localhost:3000`).

### “No data” in the UI
Most data-access endpoints are filtered by:
- `Authorization: Token <token>`
- `X-Organization-ID: <org-uuid>`

Confirm both are set (or set `REACT_APP_DEMO_AUTH_TOKEN` / `REACT_APP_ORG_ID`).

## Production / deployment notes
- Static files are served via WhiteNoise (`whitenoise` is installed and configured).
- Token auth + CORS are configured via environment variables.
- For production, set `DEBUG=False` and update security-related settings accordingly.

