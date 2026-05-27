import React from 'react';
import useUpload from '../hooks/useUpload';

const SOURCE_OPTIONS = [
  { value: 'SAP_FUEL', label: 'SAP Fuel / Procurement' },
  { value: 'UTILITY_ELECTRICITY', label: 'Utility Electricity' },
  { value: 'TRAVEL', label: 'Corporate Travel' },
];

export default function DataIngestion() {
  const {
    selectedFile,
    setSelectedFile,
    sourceType,
    setSourceType,
    uploading,
    status,
    summary,
    upload,
    reset,
  } = useUpload();

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files?.[0] || null);
  };

  const handleSubmit = async () => {
    await upload(selectedFile, sourceType);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-semibold text-slate-900">Upload ESG Data</h1>
        <p className="text-slate-500 mt-2">
          Select a source type and upload a CSV file to ingest raw records for validation and review.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {SOURCE_OPTIONS.map((source) => {
          const active = sourceType === source.value;
          return (
            <button
              key={source.value}
              type="button"
              onClick={() => setSourceType(source.value)}
              className={`border rounded-2xl p-5 text-left transition duration-200 hover:shadow-sm ${
                active ? 'border-brand-600 bg-white shadow-md' : 'border-slate-200 bg-slate-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-base font-semibold text-slate-900">{source.label}</p>
                  <p className="text-sm text-slate-500 mt-1">Upload CSV with this source format.</p>
                </div>
                <span className={`inline-flex rounded-full px-3 py-1 text-sm ${
                  active ? 'bg-brand-600 text-white' : 'bg-slate-200 text-slate-700'
                }`}>
                  {active ? 'Selected' : 'Select'}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="mt-6 border-2 border-dashed border-slate-300 rounded-2xl bg-slate-50 p-6">
        <label className="block text-sm font-medium text-slate-700 mb-3">CSV File</label>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700"
        />
        {selectedFile ? (
          <div className="mt-4 text-sm text-slate-900">
            <p className="font-medium">Selected file:</p>
            <p>{selectedFile.name}</p>
            <p className="text-slate-500">{Math.round(selectedFile.size / 1024)} KB</p>
          </div>
        ) : (
          <p className="mt-4 text-sm text-slate-500">Choose a CSV file from your computer to upload.</p>
        )}
      </div>

      <div className="mt-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={uploading}
          style={{ opacity: uploading ? 0.6 : 1 }}
          className="inline-flex items-center justify-center rounded-xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition duration-200 hover:bg-brand-700"
        >
          {uploading ? 'Uploading…' : 'Upload File'}
        </button>
        <button
          type="button"
          onClick={reset}
          className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition duration-200 hover:bg-slate-100"
        >
          Reset
        </button>
      </div>

      {status.message && (
        <div
          className={`mt-6 rounded-xl p-4 ${
            status.type === 'success'
              ? 'bg-emerald-50 text-green-700'
              : status.type === 'error'
              ? 'bg-rose-50 text-red-700'
              : 'bg-slate-100 text-slate-800'
          }`}
        >
          {status.message}
        </div>
      )}

      {summary && (
        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">Upload Summary</h2>
              <p className="text-sm text-slate-500 mt-1">Results for this import.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-medium text-slate-500">Total rows</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{summary.totalRows ?? '—'}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="text-sm font-medium text-slate-500">Succeeded</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{summary.succeeded ?? '—'}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="text-sm font-medium text-slate-500">Failed</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{summary.failed ?? '—'}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-medium text-slate-500">Flagged</p>
              <p className="mt-2 text-2xl font-semibold text-slate-900">{summary.flagged ?? '—'}</p>
            </div>
          </div>

          {summary.detail && (
            <div className="mt-5 text-sm text-slate-500">
              <p>Details sent from backend: {JSON.stringify(summary.detail)}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
