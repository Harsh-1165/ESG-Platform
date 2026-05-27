import React from 'react';
import Badge from '../ui/Badge';

export default function RecordTable({ records, loading, onRowClick, onAction }) {
  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-center">
        <div className="inline-flex items-center gap-2 text-slate-500">
          <span className="inline-block w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin"></span>
          Loading records…
        </div>
      </div>
    );
  }

  if (records.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center">
        <p className="text-slate-500">No records found. Try adjusting your filters.</p>
      </div>
    );
  }

  const getStatusVariant = (status) => {
    if (!status) return 'slate';
    if (status === 'pending') return 'pending';
    if (status === 'approved') return 'approved';
    if (status === 'rejected') return 'rejected';
    if (status === 'locked') return 'locked';
    return 'slate';
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="border-b border-slate-200 bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Source</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Facility</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Period</th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700">Quantity</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Scope</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Status</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Confidence</th>
              <th className="px-4 py-3 text-center font-semibold text-slate-700">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {records.map((record) => (
              <tr
                key={record.id}
                onClick={() => onRowClick(record)}
                className="hover:bg-slate-50 cursor-pointer transition-colors"
              >
                <td className="px-4 py-3">
                  <span className="text-slate-900 font-medium">
                    {record.source_type === 'SAP_FUEL'
                      ? 'SAP Fuel'
                      : record.source_type === 'UTILITY_ELECTRICITY'
                      ? 'Utility'
                      : 'Travel'}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-700">{record.facility_id || '—'}</td>
                <td className="px-4 py-3 text-slate-700">
                  {new Date(record.time_period).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </td>
                <td className="px-4 py-3 text-right text-slate-900 font-medium">
                  {Number(record.emission_quantity).toFixed(2)} {record.emission_unit}
                </td>
                <td className="px-4 py-3">
                  <Badge variant="slate" size="xs">
                    {record.metric_type === 'scope_1' ? 'Scope 1' : record.metric_type === 'scope_2' ? 'Scope 2' : 'Scope 3'}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  {record.approval_status ? (
                    <Badge variant={getStatusVariant(record.approval_status)} size="xs">
                      {record.approval_status === 'pending' ? 'Pending' : record.approval_status}
                    </Badge>
                  ) : (
                    <Badge variant="slate" size="xs">
                      Unreviewed
                    </Badge>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span
                    style={{
                      width: '40px',
                      height: '24px',
                      borderRadius: '4px',
                      backgroundColor: record.confidence_score > 80 ? '#ecfdf5' : record.confidence_score > 60 ? '#fefce8' : '#fff1f2',
                      color: record.confidence_score > 80 ? '#047857' : record.confidence_score > 60 ? '#d97706' : '#b91c1c',
                      fontSize: '12px',
                      fontWeight: '500',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {record.confidence_score}%
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  {record.is_suspicious && (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-red-700 bg-red-50 px-2 py-1 rounded">
                      ⚠ Flagged
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
