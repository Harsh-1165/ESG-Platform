import React from 'react';

export default function EmptyState({ title = 'No items found', description = 'Try adjusting your filters or search terms.', action }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center">
      <p className="text-xl font-semibold text-slate-900">{title}</p>
      <p className="mt-2 text-sm text-slate-600">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
