import React from 'react';

const SOURCE_OPTIONS = [
  { value: 'SAP_FUEL', label: 'SAP Fuel' },
  { value: 'UTILITY_ELECTRICITY', label: 'Utility Electricity' },
  { value: 'TRAVEL', label: 'Corporate Travel' },
];

const SCOPE_OPTIONS = [
  { value: 'scope_1', label: 'Scope 1' },
  { value: 'scope_2', label: 'Scope 2' },
  { value: 'scope_3', label: 'Scope 3' },
];

const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'locked', label: 'Locked' },
];

export default function RecordFilters({
  source,
  setSource,
  scope,
  setScope,
  status,
  setStatus,
  flagged,
  setFlagged,
  onReset,
}) {
  const activeFilterCount = [source, scope, status, flagged].filter(Boolean).length;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-slate-900">Filters</h3>
        {activeFilterCount > 0 && (
          <button
            onClick={onReset}
            className="text-sm text-brand-600 hover:text-brand-700"
          >
            Clear all ({activeFilterCount})
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Source Type</label>
          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
          >
            <option value="">All sources</option>
            {SOURCE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Scope</label>
          <select
            value={scope}
            onChange={(e) => setScope(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
          >
            <option value="">All scopes</option>
            {SCOPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Review Status</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
          >
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Flagged</label>
          <select
            value={flagged}
            onChange={(e) => setFlagged(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
          >
            <option value="">Show all</option>
            <option value="true">Flagged only</option>
            <option value="false">Not flagged</option>
          </select>
        </div>
      </div>
    </div>
  );
}
