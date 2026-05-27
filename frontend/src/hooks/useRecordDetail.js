import { useState, useEffect, useCallback } from 'react';
import { normalizationAPI, approvalAPI, auditAPI } from '../api/normalization';

export default function useRecordDetail(recordId) {
  const [record, setRecord] = useState(null);
  const [approval, setApproval] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);

  const fetchRecordDetail = useCallback(async () => {
    if (!recordId) return;
    setLoading(true);
    setError(null);
    try {
      const [recordRes, auditRes] = await Promise.all([
        normalizationAPI.getRecordDetail(recordId),
        auditAPI.getLogs(100, 0, { record_id: recordId }),
      ]);

      setRecord(recordRes.data);
      setApproval(recordRes.data.approval);
      setAuditLogs(auditRes.data.results || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching record:', err);
    } finally {
      setLoading(false);
    }
  }, [recordId]);

  useEffect(() => {
    fetchRecordDetail();
  }, [fetchRecordDetail]);

  const updateRecord = async (data) => {
    if (!recordId) return;
    setSaving(true);
    try {
      const response = await normalizationAPI.updateRecord(recordId, data);
      setRecord(response.data);
      setEditMode(false);
      await fetchRecordDetail();
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      return { success: false, error: err.message };
    } finally {
      setSaving(false);
    }
  };

  const approveRecord = async (comment = '') => {
    if (!approval?.id) return;
    setSaving(true);
    try {
      await approvalAPI.approve(approval.id, comment);
      await fetchRecordDetail();
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      return { success: false, error: err.message };
    } finally {
      setSaving(false);
    }
  };

  const rejectRecord = async (reason = '') => {
    if (!approval?.id) return;
    setSaving(true);
    try {
      await approvalAPI.reject(approval.id, reason);
      await fetchRecordDetail();
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      return { success: false, error: err.message };
    } finally {
      setSaving(false);
    }
  };

  const lockRecord = async (reason = '') => {
    if (!approval?.id) return;
    setSaving(true);
    try {
      await approvalAPI.lock(approval.id, reason);
      await fetchRecordDetail();
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      return { success: false, error: err.message };
    } finally {
      setSaving(false);
    }
  };

  return {
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
    refetch: fetchRecordDetail,
  };
}
