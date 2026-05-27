import React from 'react';

export default function DataCompare({ label, rawValue, normalizedValue, unit }) {
  const rawDisplay = rawValue === null || rawValue === undefined ? '—' : String(rawValue);
  const normalizedDisplay =
    normalizedValue === null || normalizedValue === undefined ? '—' : String(normalizedValue);
  const changed = rawDisplay !== normalizedDisplay;

  return (
    <div className="border-b border-slate-100 pb-4 mb-4 last:border-0">
      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">{label}</p>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-slate-500">Raw Value</p>
          <p className="text-sm text-slate-900 font-medium mt-1">{rawDisplay}</p>
        </div>
        <div className={changed ? 'rounded-lg bg-amber-50 p-3' : ''}>
          <p className="text-xs text-slate-500">Normalized</p>
          <p className={`text-sm font-medium mt-1 ${changed ? 'text-amber-900' : 'text-slate-900'}`}>
            {normalizedDisplay} {unit}
          </p>
          {changed && <p className="text-xs text-amber-700 mt-1">✎ Transformed</p>}
        </div>
      </div>
    </div>
  );
}
