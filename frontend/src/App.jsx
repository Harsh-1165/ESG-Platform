import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DataIngestion from './pages/DataIngestion';
import NormalizedData from './pages/NormalizedData';
import RecordDetail from './pages/RecordDetail';
import ApprovalWorkflow from './pages/ApprovalWorkflow';
import AuditLog from './pages/AuditLog';
import './App.css';
import './styles/tailwind.css';

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex' }}>
        <nav style={navStyle}>
          <h2 style={{ marginBottom: '20px' }}>ESG Platform</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li><Link to="/" style={linkStyle}>Dashboard</Link></li>
            <li><Link to="/ingestion" style={linkStyle}>Upload Data</Link></li>
            <li><Link to="/normalized" style={linkStyle}>Normalized Data</Link></li>
            <li><Link to="/approval" style={linkStyle}>Approvals</Link></li>
            <li><Link to="/audit" style={linkStyle}>Audit Log</Link></li>
          </ul>
        </nav>
        
        <main style={{ flex: 1, backgroundColor: '#fafafa' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ingestion" element={<DataIngestion />} />
            <Route path="/normalized" element={<NormalizedData />} />
            <Route path="/records/:recordId" element={<RecordDetail />} />
            <Route path="/approval" element={<ApprovalWorkflow />} />
            <Route path="/audit" element={<AuditLog />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

const navStyle = {
  width: '250px',
  backgroundColor: '#2c3e50',
  color: 'white',
  padding: '20px',
  minHeight: '100vh',
  boxShadow: '2px 0 4px rgba(0,0,0,0.1)',
};

const linkStyle = {
  color: '#ecf0f1',
  textDecoration: 'none',
  display: 'block',
  padding: '12px 0',
  borderBottom: '1px solid #34495e',
  transition: 'color 0.3s',
  fontSize: '14px',
};
