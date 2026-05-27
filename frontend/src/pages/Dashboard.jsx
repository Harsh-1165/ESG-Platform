import React, { useState, useEffect } from 'react';
import { ingestionAPI } from '../api/normalization';

export default function Dashboard() {
  const [stats] = useState({
    totalRecords: 0,
    approved: 0,
    rejected: 0,
    flagged: 0,
  });
  const [recentUploads, setRecentUploads] = useState([]);

  useEffect(() => {
    ingestionAPI.getBatches(5, 0).then((res) => {
      setRecentUploads(res.data.results);
    });
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h1>ESG Data Ingestion Platform</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px', marginBottom: '30px' }}>
        <div style={cardStyle}>
          <h3>Total Records</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{stats.totalRecords}</p>
        </div>
        <div style={cardStyle}>
          <h3>Approved</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: 'green' }}>{stats.approved}</p>
        </div>
        <div style={cardStyle}>
          <h3>Rejected</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: 'red' }}>{stats.rejected}</p>
        </div>
        <div style={cardStyle}>
          <h3>Flagged</h3>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: 'orange' }}>{stats.flagged}</p>
        </div>
      </div>
      
      <h2>Recent Uploads</h2>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th>File Name</th>
            <th>Source Type</th>
            <th>Row Count</th>
            <th>Status</th>
            <th>Uploaded</th>
          </tr>
        </thead>
        <tbody>
          {recentUploads.map((upload) => (
            <tr key={upload.id}>
              <td>{upload.file_name}</td>
              <td>{upload.source_type}</td>
              <td>{upload.row_count}</td>
              <td>{upload.status}</td>
              <td>{new Date(upload.uploaded_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const cardStyle = {
  backgroundColor: '#f5f5f5',
  borderRadius: '8px',
  padding: '20px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
};

const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  fontFamily: 'Arial, sans-serif',
};
