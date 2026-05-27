import React, { useState, useEffect } from 'react';
import { approvalAPI } from '../api/normalization';

export default function ApprovalWorkflow() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [comment, setComment] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [action, setAction] = useState(null);

  useEffect(() => {
    fetchPending();
  }, []);

  const fetchPending = async () => {
    setLoading(true);
    try {
      const response = await approvalAPI.getPending(50, 0);
      setRecords(response.data.results);
    } catch (error) {
      console.error('Error fetching pending records:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    try {
      await approvalAPI.approve(selectedRecord.id, comment);
      alert('✓ Record approved');
      setSelectedRecord(null);
      setComment('');
      fetchPending();
    } catch (error) {
      alert('✗ Error: ' + error.message);
    }
  };

  const handleReject = async () => {
    try {
      await approvalAPI.reject(selectedRecord.id, rejectReason);
      alert('✓ Record rejected');
      setSelectedRecord(null);
      setRejectReason('');
      fetchPending();
    } catch (error) {
      alert('✗ Error: ' + error.message);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Approval Workflow</h1>
      <p>{records.length} records pending review</p>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table style={tableStyle}>
          <thead>
            <tr>
              <th>Source</th>
              <th>Emission (CO2e)</th>
              <th>Facility</th>
              <th>Confidence</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.map((approval) => {
              const nr = approval.normalized_record_detail;
              return (
                <tr key={approval.id}>
                  <td>{nr.source_type}</td>
                  <td>{nr.emission_quantity} {nr.emission_unit}</td>
                  <td>{nr.facility_id}</td>
                  <td>{nr.confidence_score}%</td>
                  <td>
                    <button
                      onClick={() => setSelectedRecord(approval)}
                      style={{ padding: '5px 10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      Review
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {selectedRecord && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '8px', maxWidth: '600px', maxHeight: '80vh', overflowY: 'auto' }}>
            <h2>Review Record</h2>
            {action !== 'reject' ? (
              <>
                <div style={{ marginBottom: '20px', backgroundColor: '#f9f9f9', padding: '15px', borderRadius: '4px' }}>
                  <p><strong>Source:</strong> {selectedRecord.normalized_record_detail.source_type}</p>
                  <p><strong>Quantity:</strong> {selectedRecord.normalized_record_detail.emission_quantity} {selectedRecord.normalized_record_detail.emission_unit}</p>
                  <p><strong>Metric Type:</strong> {selectedRecord.normalized_record_detail.metric_type}</p>
                  <p><strong>Confidence Score:</strong> {selectedRecord.normalized_record_detail.confidence_score}%</p>
                </div>

                {action === 'approve' ? (
                  <div>
                    <textarea
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Optional approval comment"
                      style={{ width: '100%', padding: '10px', marginBottom: '15px', borderRadius: '4px', border: '1px solid #ddd' }}
                      rows="4"
                    />
                    <button onClick={handleApprove} style={{ ...buttonStyle, backgroundColor: 'green' }}>
                      Confirm Approve
                    </button>
                  </div>
                ) : (
                  <div>
                    <button
                      onClick={() => setAction('approve')}
                      style={{ ...buttonStyle, backgroundColor: 'green', marginRight: '10px' }}
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => setAction('reject')}
                      style={{ ...buttonStyle, backgroundColor: 'red' }}
                    >
                      Reject
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div>
                <textarea
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="Reason for rejection"
                  style={{ width: '100%', padding: '10px', marginBottom: '15px', borderRadius: '4px', border: '1px solid #ddd' }}
                  rows="4"
                />
                <button onClick={handleReject} style={{ ...buttonStyle, backgroundColor: 'red', marginRight: '10px' }}>
                  Confirm Reject
                </button>
                <button onClick={() => setAction(null)} style={{ ...buttonStyle, backgroundColor: '#6c757d' }}>
                  Cancel
                </button>
              </div>
            )}

            <button
              onClick={() => { setSelectedRecord(null); setAction(null); setComment(''); setRejectReason(''); }}
              style={{ ...buttonStyle, backgroundColor: '#6c757d', marginTop: '15px', width: '100%' }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  border: '1px solid #ddd',
};

const buttonStyle = {
  padding: '10px 20px',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
};
