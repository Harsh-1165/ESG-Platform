import React, { useState } from 'react';
import useRecords from '../hooks/useRecords';
import RecordFilters from '../components/records/RecordFilters';
import RecordSearch from '../components/records/RecordSearch';
import RecordTable from '../components/records/RecordTable';

export default function NormalizedData() {
  const [selectedRecord, setSelectedRecord] = useState(null);
  const orgId = localStorage.getItem('orgId') || '';
  const {
    records,
    loading,
    filters,
    updateFilter,
    resetFilters,
    pagination,
    goToPage,
  } = useRecords(orgId);

  const handleRowClick = (record) => {
    setSelectedRecord(record);
  };

  const handleCloseModal = () => {
    setSelectedRecord(null);
  };

  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
  const totalPages = Math.ceil(pagination.count / pagination.limit);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-semibold text-slate-900">Emission Records</h1>
        <p className="text-slate-500 mt-2">
          Review and approve normalized emission records. Total: {pagination.count} records
        </p>
      </div>

      <div className="mb-4">
        <RecordSearch
          value={filters.search}
          onChange={(val) => updateFilter('search', val)}
          onClear={() => updateFilter('search', '')}
        />
      </div>

      <div className="mb-6">
        <RecordFilters
          source={filters.source_type}
          setSource={(val) => updateFilter('source_type', val)}
          scope={filters.scope}
          setScope={(val) => updateFilter('scope', val)}
          status={filters.review_status}
          setStatus={(val) => updateFilter('review_status', val)}
          flagged={filters.flagged}
          setFlagged={(val) => updateFilter('flagged', val)}
          onReset={resetFilters}
        />
      </div>

      <RecordTable
        records={records}
        loading={loading}
        onRowClick={handleRowClick}
      />

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <p className="text-sm text-slate-500">
            Page {currentPage} of {totalPages}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => goToPage(Math.max(0, pagination.offset - pagination.limit))}
              disabled={currentPage === 1}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => goToPage(pagination.offset + pagination.limit)}
              disabled={currentPage === totalPages}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {selectedRecord && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
          <div className="rounded-2xl bg-white max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
            <div className="border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 bg-white">
              <h2 className="text-xl font-semibold text-slate-900">Record Details</h2>
              <button
                onClick={handleCloseModal}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-500">Source Type</p>
                  <p className="mt-1 text-slate-900">
                    {selectedRecord.source_type === 'SAP_FUEL'
                      ? 'SAP Fuel'
                      : selectedRecord.source_type === 'UTILITY_ELECTRICITY'
                      ? 'Utility Electricity'
                      : 'Corporate Travel'}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Period</p>
                  <p className="mt-1 text-slate-900">
                    {new Date(selectedRecord.time_period).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-500">Emission Quantity</p>
                  <p className="mt-1 text-slate-900">
                    {Number(selectedRecord.emission_quantity).toFixed(2)} {selectedRecord.emission_unit}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Scope</p>
                  <p className="mt-1 text-slate-900">
                    {selectedRecord.metric_type === 'scope_1' ? 'Scope 1' : selectedRecord.metric_type === 'scope_2' ? 'Scope 2' : 'Scope 3'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-500">Confidence Score</p>
                  <p className="mt-1 text-slate-900">{selectedRecord.confidence_score}%</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-500">Approval Status</p>
                  <p className="mt-1 text-slate-900">
                    {selectedRecord.approval_status || 'Unreviewed'}
                  </p>
                </div>
              </div>

              {selectedRecord.is_suspicious && (
                <div className="rounded-lg bg-rose-50 p-4 border border-rose-200">
                  <p className="text-sm font-medium text-red-700">⚠ Flagged for Review</p>
                </div>
              )}

              {selectedRecord.notes && (
                <div>
                  <p className="text-sm font-medium text-slate-500">Notes</p>
                  <p className="mt-1 text-slate-700">{selectedRecord.notes}</p>
                </div>
              )}

              <div className="pt-4 border-t border-slate-200">
                <button
                  onClick={handleCloseModal}
                  className="w-full rounded-lg bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-200"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
