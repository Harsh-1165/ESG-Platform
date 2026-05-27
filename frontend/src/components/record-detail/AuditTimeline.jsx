import React from 'react';

export default function AuditTimeline({ logs = [] }) {
  if (logs.length === 0) {
    return (
      <div className="text-center py-6 text-slate-500">
        <p>No audit log entries yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {logs.map((log, idx) => (
        <div key={log.id || idx} className="border-l-2 border-slate-200 pl-4 pb-4">
          <div className="flex items-baseline justify-between mb-1">
            <p className="font-semibold text-slate-900">{log.action || 'Unknown'}</p>
            <p className="text-xs text-slate-500">
              {new Date(log.timestamp).toLocaleString()}
            </p>
          </div>
          <p className="text-sm text-slate-700">By: {log.actor}</p>
          {log.reason && <p className="text-sm text-slate-600 mt-1">Reason: {log.reason}</p>}
          {log.old_values && Object.keys(log.old_values).length > 0 && (
            <div className="mt-2 text-xs bg-slate-50 border border-slate-200 rounded p-2">
              <p className="font-medium text-slate-700">Changes:</p>
              {Object.entries(log.old_values).map(([key, oldVal]) => (
                <p key={key} className="text-slate-600 mt-1">
                  {key}: <span className="text-red-600">{String(oldVal)}</span> →{' '}
                  <span className="text-green-600">{String(log.new_values?.[key] || '—')}</span>
                </p>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
