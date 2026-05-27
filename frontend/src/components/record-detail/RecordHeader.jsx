import React from 'react';
import Badge from '../ui/Badge';

export default function RecordHeader({ record, approval }) {
  if (!record) return null;

  const getStatusVariant = (status) => {
    if (!status) return 'slate';
    if (status === 'pending') return 'pending';
    if (status === 'approved') return 'approved';
    if (status === 'rejected') return 'rejected';
    if (status === 'locked') return 'locked';
    return 'slate';
  };

  return (
    <div className="border-b border-slate-200 pb-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            {record.source_type === 'SAP_FUEL'
              ? 'SAP Fuel '
              : record.source_type === 'UTILITY_ELECTRICITY'
              ? 'Utility '
              : 'Travel '}
            Emission Record
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Period: {new Date(record.time_period).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {record.is_suspicious && (
            <Badge variant="flagged" size="md">
              ⚠ Flagged
            </Badge>
          )}
          {approval?.status && (
            <Badge variant={getStatusVariant(approval.status)} size="md">
              {approval.status === 'pending' ? 'Pending Review' : approval.status}
            </Badge>
          )}
        </div>
      </div>
    </div>
  );
}
