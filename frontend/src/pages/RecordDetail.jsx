import React from 'react';
import { useParams } from 'react-router-dom';
import useRecordDetail from '../hooks/useRecordDetail';
import RecordHeader from '../components/record-detail/RecordHeader';
import DataCompare from '../components/record-detail/DataCompare';
import RecordEditForm from '../components/record-detail/RecordEditForm';
import ReviewActions from '../components/record-detail/ReviewActions';
import AuditTimeline from '../components/record-detail/AuditTimeline';

export default function RecordDetail() {
  const { recordId } = useParams();
  const {
    record,
    approval,
    auditLogs,
    loading,
    error,
    saving,
    editMode,
    setEditMode,
    updateRecord,
    approveRecord,
    rejectRecord,
    lockRecord,
  } = useRecordDetail(recordId);

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="inline-flex items-center gap-2 text-slate-500">
            <span className="inline-block w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin"></span>
            Loading record…
          </div>
        </div>
      </div>
    );
  }

  if (error || !record) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-6">
          <p className="text-red-700 font-semibold">Error loading record</p>
          <p className="text-red-600 text-sm mt-1">{error || 'Record not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <RecordHeader record={record} approval={approval} />

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Record Data</h2>

            {editMode ? (
              <RecordEditForm
                record={record}
                onSave={async (data) => {
                  const result = await updateRecord(data);
                  if (result.success) {
                    setEditMode(false);
                  }
                }}
                onCancel={() => setEditMode(false)}
                loading={saving}
              />
            ) : (
              <>
                <div className="space-y-4">
                  <DataCompare
                    label="Emission Quantity"
                    rawValue={record.emission_quantity}
                    normalizedValue={record.emission_quantity}
                    unit={record.emission_unit}
                  />
                  <DataCompare
                    label="Scope"
                    rawValue={record.metric_type}
                    normalizedValue={record.metric_type}
                  />
                  <DataCompare
                    label="Facility ID"
                    rawValue={record.facility_id}
                    normalizedValue={record.facility_id}
                  />
                  <DataCompare
                    label="Time Period"
                    rawValue={new Date(record.time_period).toLocaleDateString()}
                    normalizedValue={new Date(record.time_period).toLocaleDateString()}
                  />
                </div>

                {record.notes && (
                  <div className="mt-6 rounded-lg bg-slate-50 p-4 border border-slate-200">
                    <p className="text-xs font-semibold text-slate-600 uppercase">Notes</p>
                    <p className="text-sm text-slate-700 mt-2">{record.notes}</p>
                  </div>
                )}

                {approval?.status !== 'locked' && (
                  <button
                    onClick={() => setEditMode(true)}
                    className="mt-4 w-full rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                  >
                    ✎ Edit Record
                  </button>
                )}
              </>
            )}
          </div>

          {record.is_suspicious && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-6">
              <h3 className="font-semibold text-red-700">⚠ Validation Warnings</h3>
              <p className="text-sm text-red-600 mt-2">
                Confidence Score: <span className="font-medium">{record.confidence_score}%</span>
              </p>
            </div>
          )}

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Audit History</h3>
            <AuditTimeline logs={auditLogs} />
          </div>
        </div>

        <div className="lg:col-span-1">
          <ReviewActions
            record={record}
            approval={approval}
            onApprove={approveRecord}
            onReject={rejectRecord}
            onLock={lockRecord}
            loading={saving}
          />
        </div>
      </div>
    </div>
  );
}
