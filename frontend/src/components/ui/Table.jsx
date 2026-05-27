import React from 'react';

export default function Table({ columns = [], data = [], rowKey = 'id', onRowClick, className = '' }) {
  return (
    <div className={`overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm ${className}`}>
      <table className="min-w-full border-collapse text-sm">
        <thead className="bg-slate-50 text-left text-slate-600">
          <tr>
            {columns.map((column) => (
              <th key={column.key} className="px-4 py-3 font-semibold">
                {column.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500">
                No records to display.
              </td>
            </tr>
          ) : (
            data.map((item) => (
              <tr
                key={item[rowKey]}
                className={onRowClick ? 'cursor-pointer hover:bg-slate-50 transition-colors' : ''}
                onClick={onRowClick ? () => onRowClick(item) : undefined}
              >
                {columns.map((column) => (
                  <td key={column.key} className="px-4 py-4 align-top text-slate-700">
                    {column.render ? column.render(item) : item[column.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
