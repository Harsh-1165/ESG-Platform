import React from 'react';

const VARIANTS = {
  info: 'bg-slate-50 border-slate-200 text-slate-900',
  success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
  warning: 'bg-amber-50 border-amber-200 text-amber-800',
  error: 'bg-rose-50 border-rose-200 text-rose-800',
};

export default function AlertBox({ title, children, variant = 'info', className = '' }) {
  return (
    <div className={`rounded-2xl border px-4 py-4 ${VARIANTS[variant] || VARIANTS.info} ${className}`}>
      {title && <p className="font-semibold mb-2">{title}</p>}
      <div className="text-sm leading-relaxed">{children}</div>
    </div>
  );
}
