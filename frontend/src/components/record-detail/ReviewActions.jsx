import React, { useState } from 'react';

export default function ReviewActions({ record, approval, onApprove, onReject, onLock, loading = false }) {
  const [showApproveComment, setShowApproveComment] = useState(false);
  const [showRejectReason, setShowRejectReason] = useState(false);
  const [showLockReason, setShowLockReason] = useState(false);
  const [approveComment, setApproveComment] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [lockReason, setLockReason] = useState('');

  const isLocked = approval?.status === 'locked';
  const isApproved = approval?.status === 'approved';
  const isRejected = approval?.status === 'rejected';

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="font-semibold text-slate-900 mb-4">Review Actions</h3>

      {isLocked && (
        <div className="rounded-lg bg-slate-100 border border-slate-300 p-4 mb-4">
          <p className="text-sm font-medium text-slate-700">
            🔒 This record is locked and cannot be edited.
          </p>
          {approval?.lock_reason && (
            <p className="text-sm text-slate-600 mt-1">Reason: {approval.lock_reason}</p>
          )}
        </div>
      )}

      {isApproved && (
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-4 mb-4">
          <p className="text-sm font-medium text-green-700">
            ✓ This record is approved by {approval?.reviewer || 'an analyst'}.
          </p>
        </div>
      )}

      {isRejected && (
        <div className="rounded-lg bg-rose-50 border border-rose-200 p-4 mb-4">
          <p className="text-sm font-medium text-red-700">
            ✗ This record was rejected.
          </p>
          {approval?.rejection_reason && (
            <p className="text-sm text-red-600 mt-1">Reason: {approval.rejection_reason}</p>
          )}
        </div>
      )}

      {!isLocked && !isApproved && (
        <>
          {!showApproveComment ? (
            <button
              onClick={() => setShowApproveComment(true)}
              className="w-full rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3 text-left text-sm font-medium text-green-700 hover:bg-emerald-100 mb-3"
            >
              ✓ Approve This Record
            </button>
          ) : (
            <div className="mb-3 rounded-lg bg-emerald-50 p-4 border border-emerald-200">
              <textarea
                placeholder="Optional: Add a comment before approving…"
                value={approveComment}
                onChange={(e) => setApproveComment(e.target.value)}
                rows="2"
                className="w-full rounded-lg border border-emerald-300 bg-white px-3 py-2 text-sm text-slate-900 mb-3"
              />
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onApprove(approveComment)}
                  disabled={loading}
                  className="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                >
                  {loading ? 'Approving…' : 'Confirm Approval'}
                </button>
                <button
                  onClick={() => {
                    setShowApproveComment(false);
                    setApproveComment('');
                  }}
                  className="rounded-lg border border-emerald-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {!showRejectReason ? (
            <button
              onClick={() => setShowRejectReason(true)}
              className="w-full rounded-lg bg-rose-50 border border-rose-200 px-4 py-3 text-left text-sm font-medium text-red-700 hover:bg-rose-100 mb-3"
            >
              ✗ Reject This Record
            </button>
          ) : (
            <div className="mb-3 rounded-lg bg-rose-50 p-4 border border-rose-200">
              <textarea
                placeholder="Provide a reason for rejecting this record…"
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                rows="2"
                className="w-full rounded-lg border border-rose-300 bg-white px-3 py-2 text-sm text-slate-900 mb-3"
              />
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onReject(rejectReason)}
                  disabled={loading || !rejectReason}
                  className="rounded-lg bg-rose-600 px-3 py-2 text-xs font-semibold text-white hover:bg-rose-700 disabled:opacity-50"
                >
                  {loading ? 'Rejecting…' : 'Confirm Rejection'}
                </button>
                <button
                  onClick={() => {
                    setShowRejectReason(false);
                    setRejectReason('');
                  }}
                  className="rounded-lg border border-rose-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {!showLockReason ? (
            <button
              onClick={() => setShowLockReason(true)}
              className="w-full rounded-lg bg-slate-100 border border-slate-300 px-4 py-3 text-left text-sm font-medium text-slate-700 hover:bg-slate-200"
            >
              🔒 Lock This Record
            </button>
          ) : (
            <div className="rounded-lg bg-slate-100 p-4 border border-slate-300">
              <textarea
                placeholder="Reason for locking (optional)…"
                value={lockReason}
                onChange={(e) => setLockReason(e.target.value)}
                rows="2"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 mb-3"
              />
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onLock(lockReason)}
                  disabled={loading}
                  className="rounded-lg bg-slate-600 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-700 disabled:opacity-50"
                >
                  {loading ? 'Locking…' : 'Confirm Lock'}
                </button>
                <button
                  onClick={() => {
                    setShowLockReason(false);
                    setLockReason('');
                  }}
                  className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
