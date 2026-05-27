# ESG Data Ingestion Platform - Frontend

React frontend for ESG data ingestion and approval workflow.

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file:

```
REACT_APP_API_URL=http://localhost:8000/api
```

### 3. Start Development Server

```bash
npm start
```

App available at `http://localhost:3000`

## Pages

- **Dashboard** - Summary statistics and recent uploads
- **Upload Data** - Drag-drop CSV upload by source type
- **Normalized Data** - View normalized emission records
- **Approvals** - Analyst review queue (approve/reject)
- **Audit Log** - Complete change history

## Features

✅ Multi-page SPA with React Router  
✅ Responsive table layouts  
✅ Modal-based detail views  
✅ File upload with progress  
✅ Approval workflow UI  
✅ Real-time data fetching  

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.js       # Axios + tenant header
│   │   └── normalization.js # API methods
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── DataIngestion.jsx
│   │   ├── NormalizedData.jsx
│   │   ├── ApprovalWorkflow.jsx
│   │   └── AuditLog.jsx
│   ├── App.jsx             # Router + nav
│   ├── App.css
│   └── index.js
└── package.json
```

## Authentication

User must set org ID before using:

```javascript
localStorage.setItem('authToken', 'your-token');
localStorage.setItem('orgId', 'org-uuid');
```

Recommend adding a login page (out of MVP scope).

## API Integration

All API calls go through `src/api/client.js` which:
- Adds `Authorization: Token` header
- Adds `X-Organization-ID` header
- Handles base URL routing

## Development Notes

- **No state management**: Using local component state + React Query could be added
- **Styling**: Plain CSS, no design system (add Tailwind/Material-UI later)
- **Auth**: Hardcoded for MVP (add Auth0/JWT flow in phase 2)
- **Error handling**: Basic try/catch (add toast notifications later)

## Building for Production

```bash
npm run build
```

Output in `build/` directory. Deploy to Vercel, Netlify, or your CDN.

## Troubleshooting

**API calls fail?** Check:
- Backend is running on `http://localhost:8000`
- `X-Organization-ID` header is set
- Auth token is valid

**CORS errors?** Add origin to backend `CORS_ALLOWED_ORIGINS` setting

**Pages don't load?** Clear browser cache and localStorage

## Next Steps

1. Add authentication flow (login page)
2. Add more detailed data visualizations
3. Add export to CSV
4. Add search/filtering capabilities
5. Add real-time WebSocket updates
6. Mobile responsiveness
7. Dark mode
