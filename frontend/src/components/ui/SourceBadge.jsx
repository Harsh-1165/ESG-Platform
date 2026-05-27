import React from 'react';

const SOURCE_VARIANTS = {
  SAP_FUEL: 'bg-sky-50 text-sky-700 border border-sky-200',
  UTILITY_ELECTRICITY: 'bg-indigo-50 text-indigo-700 border border-indigo-200',
  TRAVEL: 'bg-violet-50 text-violet-700 border border-violet-200',
};

export default function SourceBadge({ sourceType, size = 'sm' }) {
  const classes = SOURCE_VARIANTS[sourceType] || 'bg-slate-50 text-slate-700 border border-slate-200';
  const sizes = {
    sm: 'px-3 py-1 text-xs',
    md: 'px-4 py-2 text-sm',
  };

  const label =
    sourceType === 'SAP_FUEL'
      ? 'SAP Fuel'
      : sourceType === 'UTILITY_ELECTRICITY'
      ? 'Utility'
      : sourceType === 'TRAVEL'
      ? 'Travel'
      : 'Unknown';

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${classes} ${sizes[size] || sizes.sm}`}>
      {label}
    </span>
  );
}
