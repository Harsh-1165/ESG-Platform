import React, { useState, useEffect } from 'react';
import { auditAPI } from '../api/normalization';

export default function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await auditAPI.getLogs(50, 0);
      setLogs(response.data.results);
    } catch (error) {
      console.error('Error fetching audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Audit Log</h1>
      <p>Total events: {logs.length}</p>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table style={tableStyle}>
          <thead>
            <tr>
              <th>Action</th>
              <th>Record Type</th>
              <th>User</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>
                  <span style={{ 
                    backgroundColor: getActionColor(log.action),
                    padding: '4px 8px',
                    borderRadius: '4px',
                    color: 'white',
                    fontSize: '12px'
                  }}>
                    {log.action}
                  </span>
                </td>
                <td>{log.record_type}</td>
                <td>{log.user}</td>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function getActionColor(action) {
  switch (action) {
    case 'approved': return '#28a745';
    case 'rejected': return '#dc3545';
    case 'locked': return '#6c757d';
    case 'created': return '#007bff';
    case 'updated': return '#ffc107';
    default: return '#6c757d';
  }
}

const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  border: '1px solid #ddd',
};
