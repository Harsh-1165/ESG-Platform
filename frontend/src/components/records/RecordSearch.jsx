import React from 'react';

export default function RecordSearch({ value, onChange, onClear }) {
  return (
    <div className="relative">
      <input
        type="text"
        placeholder="Search by facility ID, notes, or raw data…"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-600"
      />
      {value && (
        <button
          onClick={onClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700"
        >
          ✕
        </button>
      )}
    </div>
  );
}
