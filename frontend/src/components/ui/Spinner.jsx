import React from 'react';

export default function Spinner({ label = 'Loading…', size = 'md' }) {
  const dimensions = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <div className="inline-flex items-center gap-3 text-slate-600">
      <span className={`inline-block rounded-full border-2 border-slate-300 border-t-slate-700 animate-spin ${dimensions[size] || dimensions.md}`} />
      {label && <span className="text-sm font-medium">{label}</span>}
    </div>
  );
}
