import React from 'react';

export default function Badge({ children, variant = 'slate', size = 'sm' }) {
  const variants = {
    pending: 'bg-amber-50 text-amber-700 border border-amber-200',
    approved: 'bg-emerald-50 text-green-700 border border-emerald-200',
    rejected: 'bg-rose-50 text-red-700 border border-rose-200',
    locked: 'bg-slate-100 text-slate-700 border border-slate-300',
    flagged: 'bg-rose-50 text-red-700 border border-rose-200',
    slate: 'bg-slate-50 text-slate-700 border border-slate-200',
  };

  const sizes = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1 text-xs',
    md: 'px-4 py-2 text-sm',
  };

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${variants[variant] || variants.slate} ${sizes[size] || sizes.sm}`}>
      {children}
    </span>
  );
}
